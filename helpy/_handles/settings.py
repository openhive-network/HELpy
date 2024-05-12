from __future__ import annotations

from pathlib import Path

from pydantic import Field

from helpy._communication.abc.communicator import AbstractCommunicator  # noqa: TCH001
from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.url import HttpUrl  # noqa: TCH001


class HandleSettings(CommunicationSettings):
    http_endpoint: HttpUrl
    communicator: type[AbstractCommunicator] | AbstractCommunicator | None = None
    working_directory: Path = Field(default_factory=lambda: Path("."))

    def try_get_communicator_instance(
        self, settings: CommunicationSettings | None = None
    ) -> AbstractCommunicator | None:
        if self.communicator is None:
            return None

        if isinstance(self.communicator, type):
            return self.communicator(settings=(settings or self))

        return self.communicator
