from __future__ import annotations

from datetime import timedelta
from distutils.util import strtobool
from pathlib import Path
from typing import ClassVar

from beekeepy._communication.abc.communicator import AbstractCommunicator  # noqa: TCH001
from beekeepy._interface.url import HttpUrl  # noqa: TCH001
from beekeepy._remote_handle.settings import Settings as RemoteHandleSettings


class Settings(RemoteHandleSettings):
    """Defines parameters for beekeeper how to start and behave."""

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

    http_endpoint: HttpUrl | None = None  # type: ignore[assignment]
    """
    Endpoint on which python will communicate with beekeeper, required for remote beekeeper.
    In case of local beekeeper, this address will be used for beekeeper to start listening on.
    """

    communicator: type[AbstractCommunicator] | AbstractCommunicator | None = None
    """
    Defines class to be used for network handling. Can be given as class or instance.

    Note: If set to none, handles will use preferred communicators
    """

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

    initialization_timeout: timedelta = Defaults.default_factory(
        EnvironNames.INITIALIZATION_TIMEOUT,
        lambda x: (Settings.Defaults.INITIALIZATION_TIMEOUT if x is None else timedelta(seconds=int(x))),
    )

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
