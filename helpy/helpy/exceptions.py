from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Sequence

from helpy._interfaces.url import Url

if TYPE_CHECKING:
    from helpy._interfaces.url import Url

Json = dict[str, Any]
CommunicationResponseT = str | Json | list[Json]


class HelpyError(Exception):
    """Base class for all helpy Errors."""

    @property
    def cause(self) -> BaseException | None:
        return self.__cause__


class UnknownDecisionPathError(HelpyError):
    """Error created to suppress mypy error: `Missing return statement  [return]`."""


class ParseError(HelpyError):
    """Raised if cannot parse given str, e.x. url, date, asset."""


class BlockWaitTimeoutError(HelpyError):
    """Raised if reached not expected block number."""

    def __init__(
        self,
        last_block_number: int,
        block_number: int,
        last_irreversible_block_number: int,
    ) -> None:
        """Creates exception.

        Args:
            last_block_number: last fetched block number
            block_number: block that was expected to be irreversible
            last_irreversible_block_number: last fetched irreversible block number
        """
        super().__init__(
            f"Block with number `{last_block_number}` was just reached but expected `{block_number}` is still not"
            " irreversible.\n"
            f"Last irreversible block number is `{last_irreversible_block_number}`."
        )


class BatchRequestError(HelpyError):
    """Base class for batch related errors."""


class NothingToSendError(BatchRequestError):
    """Raised if there is nothing to send, example.

    with node.batch():
        pass
        # here on exit NothingToSendError will be raised
    """


class ResponseNotReadyError(BatchRequestError):
    """Raised on access to response when it's not ready.

    with node.batch() as x:
        resp = x.api.some_endpoint()
        assert resp.some_var == 1  # here ResponseNotReadyError will be raised
    """


class CommunicationError(HelpyError):
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


class ExceededAmountOfRetriesError(CommunicationError):
    """Raised if exceeded amount of retries."""


class TimeoutExceededError(CommunicationError):
    """Raised if exceeded time for response."""

    def __init__(  # noqa: PLR0913
        self,
        url: str | Url[Any],
        request: CommunicationResponseT | bytes,
        response: CommunicationResponseT | None = None,
        *,
        message: str = "",
        timeout_secs: float | None = None,
        total_wait_time: float | None = None,
    ) -> None:
        message += f"\ntimeout was set to: {timeout_secs}s" if timeout_secs is not None else ""
        message += f"\ntotal wait time: {total_wait_time}s" if total_wait_time is not None else ""
        super().__init__(url, request, response, message=message)
        self.timeout_secs = timeout_secs
        self.total_wait_time = total_wait_time


class InvalidOptionError(HelpyError):
    """Raised if invalid expression is given in config."""


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


class UnableToAcquireDatabaseLockError(OverseerError):
    def retry(self) -> bool:
        return True


class UnableToAcquireForkdbLockError(OverseerError):
    def retry(self) -> bool:
        return True


class NullResultError(OverseerError):
    def retry(self) -> bool:
        return True


class ApiNotFoundError(OverseerError):
    def retry(self) -> bool:
        return False

    @property
    def api(self) -> str:
        return self.message_raw.split(":")[-1].strip()


class JussiResponseError(OverseerError):
    def retry(self) -> bool:
        return True


class UnparsableResponseError(OverseerError):
    def retry(self) -> bool:
        return True


class DifferenceBetweenAmountOfRequestsAndResponsesError(OverseerError):
    def retry(self) -> bool:
        return True


class UnlockIsNotAccessibleError(OverseerError):
    def retry(self) -> bool:
        return False


class WalletIsAlreadyUnlockedError(OverseerError):
    def retry(self) -> bool:
        return False


class UnableToOpenWalletError(OverseerError):
    def retry(self) -> bool:
        return False


class InvalidPasswordError(OverseerError):
    def retry(self) -> bool:
        return False


class ErrorInResponseError(OverseerError):
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
        super().__init__(
            url=url,
            request=request,
            response=response,
            message=message,
            request_id=request_id,
            whole_response=whole_response,
        )
        self.__error: str | None = None

    def retry(self) -> bool:
        return False

    @property
    def error(self) -> str:
        if self.__error is None:
            result = self._extract_error_messages(response=self.__get_suitable_response())
            self.__error = (result or [""])[0]
        return self.__error

    def __get_suitable_response(self) -> Json | str | None:
        if isinstance(self.response, list):
            if self.request_id is None:
                return None
            for item in self.response:
                if item.get("id", {}) == self.request_id:
                    return item
            return None
        return self.response


class GroupedErrorsError(HelpyError):
    def __init__(self, exceptions: Sequence[Exception]) -> None:
        self.exceptions = list(exceptions)

    def get_exception_for(self, *, request_id: int) -> OverseerError | None:
        for exception in self.exceptions:
            if isinstance(exception, OverseerError) and exception.request_id == request_id:
                return exception
        return None
