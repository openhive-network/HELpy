from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import Field

from beekeepy._communication.settings import CommunicationSettings

if TYPE_CHECKING:
    from beekeepy._communication.abc.communicator import AbstractCommunicator
    from beekeepy._interface.url import HttpUrl


class Settings(CommunicationSettings):
    """Defines parameters for beekeeper how to start and behave."""

    working_directory: Path = Field(default_factory=lambda: Path.cwd())
    """Path, where beekeeper binary will store all it's data and logs."""

    http_endpoint: HttpUrl | None = None
    """Endpoint on which python will communicate with beekeeper, required for remote beekeeper."""

    communicator: type[AbstractCommunicator] | AbstractCommunicator | None = None
    """
    Defines class to be used for network handling. Can be given as class or instance.

    Note: If set to none, handles will use preferred communicators
    """

    notification_endpoint: HttpUrl | None = None
    """Endpoint to use for reverse communication between beekeeper and python."""

    binary_path: Path | None = None
    """Alternative path to beekeeper binary."""

    propagate_sigint: bool = True
    """If set to True (default), sigint will be sent to beekeeper without control of this library."""

    use_existing_session: str | None = None
    """If set, beekeeper will use given session while connecting to beeekeeper."""

    close_timeout: timedelta = Field(default_factory=lambda: timedelta(seconds=10.0))
    """This timeout varriable affects time handle waits before beekeepy closes."""

    def try_get_communicator_instance(
        self, settings: CommunicationSettings | None = None
    ) -> AbstractCommunicator | None:
        """Tries to return instance of communicator.

        If communicator is given as class, such instance will be created,
        by passing keyword argument: settings=settings,
        where value of settings is get from function arguments.

        Args:
            settings: Used for communicator instance creation.
                When None is passed, settings will be filled with current instance of settings (self)

        Returns:
            Child of AbstractCommunicator instance if communicator is not None, otherwise None
        """
        if self.communicator is None:
            return None

        if isinstance(self.communicator, type):
            return self.communicator(settings=(settings or self))

        return self.communicator
