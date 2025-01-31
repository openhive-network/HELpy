from __future__ import annotations

from datetime import timedelta
from distutils.util import strtobool
from pathlib import Path
from typing import ClassVar

from helpy import HttpUrl
from helpy import Settings as HandleSettings


class Settings(HandleSettings):
    """Defines parameters for beekeeper how to start and behave."""

    class EnvironNames(HandleSettings.EnvironNames):
        WORKING_DIRECTORY: ClassVar[str] = "BEEKEEPY_WORKING_DIRECTORY"
        PROPAGATE_SIGINT: ClassVar[str] = "BEEKEEPY_PROPAGATE_SIGINT"
        CLOSE_TIMEOUT: ClassVar[str] = "BEEKEEPY_CLOSE_TIMEOUT"

    class Defaults(HandleSettings.Defaults):
        WORKING_DIRECTORY: ClassVar[Path] = Path.cwd()
        PROPAGATE_SIGINT: ClassVar[bool] = True
        CLOSE_TIMEOUT: ClassVar[timedelta] = timedelta(seconds=10.0)

    working_directory: Path = Defaults.default_factory(
        EnvironNames.WORKING_DIRECTORY,
        lambda x: (Settings.Defaults.WORKING_DIRECTORY if x is None else Path(x)),
    )
    """Path, where beekeeper binary will store all it's data and logs."""

    http_endpoint: HttpUrl | None = None  # type: ignore[assignment]
    """Endpoint on which python will communicate with beekeeper, required for remote beekeeper."""

    notification_endpoint: HttpUrl | None = None
    """Endpoint to use for reverse communication between beekeeper and python."""

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
