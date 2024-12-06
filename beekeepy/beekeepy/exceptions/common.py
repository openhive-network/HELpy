from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Final

from beekeepy.exceptions.base import (
    BeekeeperExecutableError,
    BeekeeperHandleError,
    BeekeepyError,
    InvalidatedStateError,
)

if TYPE_CHECKING:
    from beekeepy._interface.url import Url


JsonT = dict[str, Any]
CommunicationResponseT = str | JsonT | list[JsonT]


class CommunicationError(BeekeepyError):
    """Base class for all communication related errors."""

    def __init__(
        self,
        url: str | Url[Any],
        request: str | bytes,
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


class RequestError(BeekeepyError):
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


class BatchRequestError(BeekeepyError):
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


class BeekeeperIsNotRunningError(BeekeeperExecutableError):
    """Raises if after user tries to access options available only when process is running."""


class BeekeeperFailedToStartError(BeekeeperExecutableError):
    """Raises if beekeeper exited with non-0 exit code."""


class WalletIsLockedError(BeekeepyError):
    """Raises if marked function requires wallet to be unlocked."""

    def __init__(self, wallet_name: str) -> None:
        """Constructor."""
        self.wallet_name = wallet_name
        super().__init__(f"Wallet `{wallet_name}` is locked.")


class TimeoutReachWhileCloseError(BeekeepyError):
    """Raises when beekeeper did not closed during specified timeout."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__("Process was force-closed with SIGKILL, because didn't close before timeout")


class UnknownDecisionPathError(BeekeepyError):
    """Error created to suppress mypy error: `Missing return statement  [return]`."""


class NotPositiveTimeError(BeekeepyError):
    """Raises when given time value was 0 or negative."""

    def __init__(self, time: int) -> None:
        """Constructor.

        Args:
            time (int): invalid time value
        """
        super().__init__(f"Given time value is not positive: `{time}`.")


class TimeTooBigError(BeekeepyError):
    """Raises when given time value was 2^32 or higher."""

    MAX_VALUE: Final[int] = 2**32

    def __init__(self, time: int) -> None:
        """Constructor.

        Args:
            time (int): invalid time value
        """
        super().__init__(f"Given time value is too big: `{time}` >= {TimeTooBigError.MAX_VALUE}.")


class InvalidWalletNameError(BeekeepyError):
    """Raises when specified wallet name was not matching alphanumeric and extra characters conditions."""

    def __init__(self, wallet_name: str) -> None:
        """Constructor.

        Args:
            wallet_name (str): invalid wallet name
        """
        super().__init__(
            f"Given wallet name is invalid: `{wallet_name}`. Can be only alphanumeric or contain `._-@` characters."
        )


class DetachRemoteBeekeeperError(BeekeeperHandleError):
    """Raises when user tries to detach beekeeper that is remote."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__(
            "Cannot detach remote beekeeper, as this handle does not own process and cannot manage process of beekeeper"
            " that is referring through web"
        )


class InvalidatedStateByClosingBeekeeperError(InvalidatedStateError):
    """Raises when beekeeper user want to interact with beekeeper, but it was invalidated by closing beekeeper."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__(
            invalidated_by="calling teardown on beekeeper object",
            how_to="call again one of Beekeeper.factory or Beekeeper.remote_factory method to create new beekeeper",
        )


class InvalidatedStateByClosingSessionError(InvalidatedStateError):
    """Raises when beekeeper user want to interact with session dependent objects,
    but it was invalidated by closing session.
    """  # noqa: D205

    def __init__(self) -> None:
        """Constructor."""
        super().__init__(
            invalidated_by="calling close_session on session objecct",
            how_to="creating new session again by calling beekeeper.create_session",
        )


class InvalidOptionError(BeekeepyError):
    """Raised if invalid expression is given in config."""
