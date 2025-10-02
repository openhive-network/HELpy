from __future__ import annotations

from beekeepy.exceptions import ExecutableError, ProcessSearchError


class TimeoutReachWhileCloseError(ExecutableError):
    """Raises when executable did not closed during specified timeout."""

    def __init__(self) -> None:
        super().__init__("Process was force-closed with SIGKILL, because didn't close before timeout")


class ExecutableIsNotRunningError(ExecutableError):
    """Raises when executable is not running, but user requests action on running instance."""


class FailedToStartExecutableError(ExecutableError):
    """Raises when executable failed to start."""


class FailedToDetectReservedPortsError(ExecutableError):
    """Raises when port lookup procedure fails."""


class FailedToDetectRunningBeekeeperError(ProcessSearchError):
    """Raises when no matching instances of beekeeper left after filtering out on given criteria."""


class UndistinguishableBeekeeperInstancesError(ProcessSearchError):
    """Raises when multiple instances of beekeeper were found after filtering out on given criteria."""
