from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from beekeepy._utilities.context import ContextSync

if TYPE_CHECKING:
    from types import TracebackType

    from beekeepy._communication import Url

Json = dict[str, Any]
CommunicationResponseT = str | Json | list[Json]
BaseOfAllExceptions = Exception


class BeekeepyError(BaseOfAllExceptions, ABC):
    """Base class for all exception raised by beekeepy."""

    @property
    def cause(self) -> BaseException | None:
        return self.__cause__


class BeekeeperExecutableError(BeekeepyError, ABC):
    """Base class for exceptions related to starting/closing beekeeper executable."""


class BeekeeperHandleError(BeekeepyError, ABC):
    """Base class for exceptions related to beekeeper handle."""


class BeekeeperInterfaceError(BeekeepyError, ABC):
    """Base class for exceptions related to beekeeper interface."""


class DetectableError(ContextSync[None], BeekeeperInterfaceError, ABC):
    """
    Base class for conditionally raised exception using `with` statement based detection.

    Example:
    ```
    with DividsionByZeroException(a, b):
        print(a / b)
    ```

    Raises:
        self: If conditions specified by child classes in `_is_exception_handled` are met
    """

    @abstractmethod
    def _is_exception_handled(self, ex: BaseException) -> bool: ...

    def _enter(self) -> None:
        return None

    def _finally(self) -> None:
        return None

    def _handle_exception(self, ex: BaseException, tb: TracebackType | None) -> bool:
        if self._is_exception_handled(ex):
            raise self from ex
        return super()._handle_exception(ex, tb)


class SchemaDetectableError(DetectableError, ABC):
    """Base class for errors that bases on schema exceptions."""

    def __init__(self, arg_name: str, arg_value: str) -> None:
        """Constructor.

        Args:
            arg_name (str): name of argument which was invalid
            arg_value (str): value of argument which was invalid
        """
        self._arg_name = arg_name
        self._arg_value = arg_value
        super().__init__(self._error_message())

    def _is_exception_handled(self, ex: BaseException) -> bool:
        return isinstance(ex, ValueError)

    @abstractmethod
    def _error_message(self) -> str: ...


class InvalidatedStateError(BeekeeperInterfaceError):
    """Raised if state has been invalidated."""

    def __init__(self, invalidated_by: str | None = None, how_to: str | None = None) -> None:
        """Constructor."""
        super().__init__(
            "Object is now in invalidated state, it can no longer be used."
            + (f"It was invalidated by {invalidated_by}." if invalidated_by else "")
            + (f"To gain access again, you have to {how_to}." if how_to else "")
        )


class BeekeeperFailedToStartError(BeekeeperExecutableError):
    """Base class for errors while launching beekeeper."""


class CommunicationError(BeekeepyError):
    """Base class for all communication related errors."""

    def __init__(
        self,
        url: str | Url[Any],
        request: CommunicationResponseT | bytes,
        response: CommunicationResponseT | None = None,
        *,
        message: str = "",
    ) -> None:
        """Contains required details.

        Args:
            url: where request has been send
            request: content of request
            response: content of response. Defaults to None.
            message: additional information about error. Defaults to "".
        """
        self.url = str(url)
        self.request = request
        self.response = response
        self.message_raw = message
        self.message = self.__create_message(self.message_raw)
        super().__init__(self.message, self.url, self.request, self.response)

    def get_response_error_messages(self) -> list[str]:
        return CommunicationError._extract_error_messages(self.response)

    @classmethod
    def _extract_error_messages(cls, response: CommunicationResponseT | None) -> list[str]:
        """Obtains error message from response."""
        if response is None:
            return []

        if isinstance(response, str):
            """
            Do not parse, as `str` is passed only in case
            of unparsable response.
            """
            return [response]

        if isinstance(response, dict):
            message = response.get("error", {}).get("message", None)
            return [str(message)] if message is not None else []

        if isinstance(response, list):
            messages = []
            for item in response:
                if messages_recurrence := cls._extract_error_messages(item):
                    messages.extend(messages_recurrence)
            return messages

        raise TypeError(f"Unsupported type: {type(response)}")

    def _get_reply(self) -> str:
        if self.response is not None:
            return f"{self.response=}"

        return "no response available"

    def __create_message(self, message: str) -> str:
        return (
            (message + "\n\n") if message else ""
        ) + f"Problem occurred during communication with: url={self.url}, request={self.request!r}, {self._get_reply()}"


class OverseerError(CommunicationError, ABC):
    """Base class for exceptions dedicated to be raised on invalid content in response."""

    def __init__(  # noqa: PLR0913
        self,
        url: str | Url[Any],
        request: CommunicationResponseT | bytes,
        response: CommunicationResponseT | None = None,
        whole_response: CommunicationResponseT | None = None,
        *,
        message: str = "",
        request_id: int | None,
    ) -> None:
        super().__init__(url, request, response, message=message)
        self.request_id = request_id
        self.whole_response = whole_response

    @abstractmethod
    def retry(self) -> bool:
        """Used by overseer to determine if retry should be performed if such error occurs."""


class ExecutableError(BeekeepyError, ABC):
    """Base class for errors related to handling executable."""


class ProcessSearchError(ExecutableError, ABC):
    """Base class for error related to looking up for process."""
