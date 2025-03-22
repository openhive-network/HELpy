from __future__ import annotations

from beekeepy.exceptions.base import ExecutableError


class TimeoutReachWhileCloseError(ExecutableError):
    """Raises when executable did not closed during specified timeout."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__("Process was force-closed with SIGKILL, because didn't close before timeout")


class ExecutableIsNotRunningError(ExecutableError):
    """Raises when executable is not running, but user requests action on running instance."""


class FailedToStartExecutableError(ExecutableError):
    """Raises when executable failed to start."""


class FailedToDetectReservedPortsError(ExecutableError):
    """Raises when port lookup procedure fails."""
