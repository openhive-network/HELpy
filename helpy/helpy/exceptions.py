from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Sequence

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


class RequestError(HelpyError):
    """Raised if error field is in the response."""

    def __init__(self, send: str, error: str | JsonT) -> None:
        """
        Initialize a RequestError.

        Parameters:
        - send (str): The request sent.
        - error (str | JsonT): The error received in response.

        Returns:
        None
        """
        self.send = send
        self.error = self.__try_extract_exception_message(error)
        super().__init__(f"{send=} | {self.error=}")

    def __try_extract_exception_message(self, error: str | JsonT) -> str | JsonT:
        try:
            parsed_error = json.loads(error) if isinstance(error, str) else error
            if not isinstance(error, dict):
                return error
            return parsed_error.get("message", error)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return error


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
        message = message or self.__create_message()
        super().__init__(message)

    def get_response_error_messages(self) -> list[str]:
        """Obtains error message from response."""
        result = self.get_response()
        if result is None:
            return []

        if isinstance(result, dict):
            message = result.get("error", {}).get("message", None)
            return [str(message)] if message is not None else []

        messages = []
        for item in result:
            message = item.get("error", {}).get("message", None)
            if message is not None:
                messages.append(str(message))
        return messages

    def get_response(self) -> JsonT | list[JsonT] | None:
        return self.response if isinstance(self.response, dict | list) else None

    def _get_reply(self) -> str:
        if (result := self.get_response()) is not None:
            return f"response={result}"

        if self.response is not None:
            return f"response={self.response}"

        return "no response available"

    def __create_message(self) -> str:
        return (
            f"Problem occurred during communication with: url={self.url}, request={self.request!r}, {self._get_reply()}"
        )


class ExceededAmountOfRetriesError(CommunicationError):
    """Raised if exceeded amount of retries."""


class TimeoutExceededError(CommunicationError):
    """Raised if exceeded time for response."""


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
    def retry(self) -> bool: ...


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
            url,
            request,
            response,
            message=message,
            request_id=request_id,
            whole_response=whole_response,
        )
        self.__error: str | None = None

    def retry(self) -> bool:
        return False


class GroupedErrorsError(HelpyError):
    def __init__(self, exceptions: Sequence[Exception]) -> None:
        self.exceptions = list(exceptions)

    def get_exception_for(self, *, request_id: int) -> OverseerError | None:
        for exception in self.exceptions:
            if isinstance(exception, OverseerError) and exception.request_id == request_id:
                return exception
        return None
