from __future__ import annotations

from typing import Final

from beekeepy.exceptions.base import (
    BeekeeperExecutableError,
    BeekeeperHandleError,
    BeekeepyError,
    InvalidatedStateError,
)


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
