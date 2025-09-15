from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Sequence

from beekeepy._communication.abc.rules import ContinueMode
from beekeepy._utilities.context import SelfContextSync
from beekeepy.exceptions import GroupedErrorsError, Json, UnknownDecisionPathError

if TYPE_CHECKING:
    from types import TracebackType

    from beekeepy._communication.abc.communicator import AbstractCommunicator
    from beekeepy._communication.abc.communicator_models import AsyncCallbacks, Callbacks, Methods
    from beekeepy._communication.abc.rules import Rules, RulesClassifier
    from beekeepy._communication.url import HttpUrl
    from beekeepy.exceptions import OverseerError


__all__ = ["AbstractOverseer"]


class _OverseerExceptionManager(SelfContextSync):
    """This class should be considered as part of AbstractOverseer.

    Note: Not intended for public use.
    """

    EXIT_LOOP: ClassVar[bool] = False
    CONTINUE_LOOP: ClassVar[bool] = True

    def __init__(self, owner: AbstractOverseer, rules: Rules) -> None:
        super().__init__()
        self._owner = owner
        self._rules = rules
        self._exception_rules = rules.grouped_exceptions()
        self._exceptions: Sequence[OverseerError] = []
        self._last_status = ContinueMode.INF
        self._counter = 0
        self._last_parsed_response: Json | list[Json] | Exception = {}
        self._response_read_or_exception_occurred = False
        self._reset_counter()

    @property
    def response(self) -> Json | list[Json]:
        self._response_read_or_exception_occurred = True
        return {} if isinstance(self._last_parsed_response, Exception) else self._last_parsed_response

    @property
    def exceptions(self) -> list[OverseerError]:
        return list(self._exceptions)

    def update(self, response: str) -> None:
        self._last_parsed_response = self._owner._parse(response)
        self._exceptions, self._last_status = self._owner._oversee(
            rules=self._rules,
            response=self._last_parsed_response,
            response_raw=response,
        )

    def continue_loop(self) -> bool:
        if self._last_status == ContinueMode.INF:
            self._reset_counter()
            return self.CONTINUE_LOOP

        if self._last_status == ContinueMode.BREAK:
            if self._exceptions:
                self.__raise()
            return self.EXIT_LOOP

        if not self._exceptions:
            return self.EXIT_LOOP
        self._counter -= 1

        if self._counter < 0:
            self.__raise()
        return self.CONTINUE_LOOP

    def should_sleep(self) -> bool:
        if len(self._exceptions) == 0:
            # No exceptions, no need to sleep
            return False
        for exception in self._exceptions:
            if type(exception) in self._exception_rules.preliminary:
                # Preliminary exception, no need to sleep
                return False
            if self._counter <= 0 and type(exception) in self._exception_rules.finitely_repeatable:
                # Finitely repeatable exception, but no retries left, no need to sleep
                return False
        return True

    def _finally(self) -> None:
        if not self._response_read_or_exception_occurred:
            if self._exceptions:
                self.__raise()
            raise UnknownDecisionPathError("Neither exception nor result has not been read") from self.__grouped_error()

    def _handle_exception(self, ex: BaseException, tb: TracebackType | None) -> bool:
        self._response_read_or_exception_occurred = True
        return super()._handle_exception(ex, tb)

    def __raise(self) -> None:
        raise self._exceptions[0] from self.__grouped_error()

    def __grouped_error(self) -> GroupedErrorsError:
        return GroupedErrorsError(self._exceptions)

    def _reset_counter(self) -> None:
        self._counter = self._owner.communicator.settings.max_retries


class AbstractOverseer(ABC):
    def __init__(
        self,
        *args: Any,
        communicator: AbstractCommunicator,
        json_loads: Callable[[str], Json | list[Json]] = json.loads,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.communicator = communicator
        self._json_loads = json_loads

    def send(
        self, url: HttpUrl, method: Methods, data: str | None = None, callbacks: Callbacks | None = None
    ) -> Json | list[Json]:
        with _OverseerExceptionManager(owner=self, rules=self.__rules(url=url, request=data)) as mgr:
            while mgr.continue_loop():
                response = self.communicator.send(url=url, method=method, data=data, callbacks=callbacks)
                mgr.update(response)
                if mgr.should_sleep():
                    self._sleep_for_retry()
            return mgr.response
        raise self._unknown_decision_path_after_exiting_context("send")

    async def async_send(
        self, url: HttpUrl, method: Methods, data: str | None = None, callbacks: AsyncCallbacks | None = None
    ) -> Json | list[Json]:
        with _OverseerExceptionManager(owner=self, rules=self.__rules(url=url, request=data)) as mgr:
            while mgr.continue_loop():
                response = await self.communicator.async_send(url=url, method=method, data=data, callbacks=callbacks)
                mgr.update(response)
                if mgr.should_sleep():
                    await self._async_sleep_for_retry()
            return mgr.response
        raise self._unknown_decision_path_after_exiting_context("async_send")

    @abstractmethod
    def _rules(self) -> RulesClassifier: ...

    def __rules(self, url: HttpUrl, request: str | None) -> Rules:
        return self._rules().instantiate(url=url, request=self._json_loads(request) if request else None)

    def _oversee(
        self, rules: Rules, response: Json | list[Json] | Exception, response_raw: str
    ) -> tuple[list[OverseerError], ContinueMode]:
        exceptions: list[OverseerError] = []
        result_status: ContinueMode = ContinueMode.INF

        for rule, status in rules.resolved_rules():
            exceptions_to_add = rule.check(response=response, response_raw=response_raw)
            exceptions.extend(exceptions_to_add)
            result_status = min(result_status, status)
            for ex in exceptions_to_add:
                if not ex.retry():
                    return (exceptions, status)

        return (exceptions, result_status) if bool(exceptions) else ([], ContinueMode.CONTINUE)

    def _parse(self, response: str) -> Json | list[Json] | Exception:
        response_parsed: Json | list[Json] | None = None
        error_from_parsing: Exception | None = None
        try:
            response_parsed = self._json_loads(response)
        except json.JSONDecodeError as error:
            error_from_parsing = error

        response_for_rules = response_parsed or error_from_parsing
        if response_for_rules is None:
            raise UnknownDecisionPathError("After parsing, both result and error is None")
        return response_for_rules

    def teardown(self) -> None:
        self.communicator.teardown()

    def _unknown_decision_path_after_exiting_context(self, func: str) -> UnknownDecisionPathError:
        return UnknownDecisionPathError(
            "Exited _OverseerExceptionManager context without raising"
            f"any exception nor returning any value in {type(self)}:{func}"
        )

    async def _async_sleep_for_retry(self) -> None:
        """Sleeps using asyncio.sleep (for asynchronous implementations)."""
        await asyncio.sleep(self.communicator.settings.period_between_retries.total_seconds())

    def _sleep_for_retry(self) -> None:
        """Sleeps using time.sleep (for synchronous implementations)."""
        time.sleep(self.communicator.settings.period_between_retries.total_seconds())
