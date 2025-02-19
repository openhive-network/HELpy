from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from beekeepy.exceptions.base import (
    BeekeeperExecutableError,
    BeekeeperFailedToStartError,
    BeekeeperHandleError,
    BeekeepyError,
    CommunicationError,
    CommunicationResponseT,
    InvalidatedStateError,
)

if TYPE_CHECKING:
    from beekeepy._interface.url import Url


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


class BeekeeperFailedToStartDuringProcessSpawnError(BeekeeperFailedToStartError):
    """Raises if beekeeper exited with non-0 exit code during startup."""


class BeekeeperFailedToStartNotReadyOnTimeError(BeekeeperFailedToStartError):
    """Raises if beekeeper didn't start on time."""


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


class UnknownDecisionPathError(BeekeepyError):
    """Error created to suppress mypy error: `Missing return statement  [return]`."""


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
