from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import ClassVar

from beekeepy._communication import HttpUrl  # noqa: TCH001
from beekeepy._remote_handle import RemoteHandleSettings
from beekeepy.exceptions import UnknownValueForBooleanConversionError


def strtobool(value: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    This is a simple implementation, similar to distutils.util.strtobool.

    NOTE: This function is replacement for distutils.util.strtobool,
        which is deprecated and slow to import.
    """
    val = value.lower()
    if val in ("y", "yes", "true", "t", "1"):
        return True
    if val in ("n", "no", "false", "f", "0"):
        return False
    raise UnknownValueForBooleanConversionError(value)


class Settings(RemoteHandleSettings):
    """Defines parameters for runnable handles how to start and behave."""

    class EnvironNames(RemoteHandleSettings.EnvironNames):
        WORKING_DIRECTORY: ClassVar[str] = "BEEKEEPY_WORKING_DIRECTORY"
        PROPAGATE_SIGINT: ClassVar[str] = "BEEKEEPY_PROPAGATE_SIGINT"
        CLOSE_TIMEOUT: ClassVar[str] = "BEEKEEPY_CLOSE_TIMEOUT"
        INITIALIZATION_TIMEOUT: ClassVar[str] = "BEEKEEPY_INITIALIZATION_TIMEOUT"

    class Defaults(RemoteHandleSettings.Defaults):
        WORKING_DIRECTORY: ClassVar[Path] = Path.cwd()
        PROPAGATE_SIGINT: ClassVar[bool] = True
        CLOSE_TIMEOUT: ClassVar[timedelta] = timedelta(seconds=10.0)
        INITIALIZATION_TIMEOUT: ClassVar[timedelta] = timedelta(seconds=5.0)

    working_directory: Path | None = None
    """Path, where beekeeper binary will store all it's data and logs."""

    http_endpoint: HttpUrl | None = None
    """
    Endpoint on which python will communicate with beekeeper, required for remote beekeeper.
    In case of local beekeeper, this address will be used for beekeeper to start listening on.
    """

    binary_path: Path | None = None
    """Alternative path to beekeeper binary."""

    propagate_sigint: bool = Defaults.default_factory(
        EnvironNames.PROPAGATE_SIGINT,
        lambda x: (Settings.Defaults.PROPAGATE_SIGINT if x is None else strtobool(x)),
    )
    """If set to True (default), sigint will be sent to beekeeper without control of this library."""

    use_existing_session: str | None = None
    """If set, beekeeper will use given session while connecting to beeekeeper."""

    close_timeout: timedelta = Defaults.default_factory(
        EnvironNames.CLOSE_TIMEOUT,
        lambda x: (Settings.Defaults.CLOSE_TIMEOUT if x is None else timedelta(seconds=int(x))),
    )
    """Affects time handle waits before beekeepy closes."""

    initialization_timeout: timedelta = Defaults.default_factory(
        EnvironNames.INITIALIZATION_TIMEOUT,
        lambda x: (Settings.Defaults.INITIALIZATION_TIMEOUT if x is None else timedelta(seconds=int(x))),
    )
    """Affects time handle waits for beekeeper to start."""

    @property
    def ensured_working_directory(self) -> Path:
        """This property should be used to make sure, that path to working dir is returned.

        Note: If Settings.working_directory is not set, Path.cwd() is returned.
        """
        return self.working_directory or Settings.Defaults.WORKING_DIRECTORY

    @property
    def ensured_http_endpoint(self) -> HttpUrl:
        """Returns Settings.http_endpoint, if set to None, raises Exception."""
        if self.http_endpoint is None:
            raise ValueError("Settings.http_endpoint is None")

        return self.http_endpoint
