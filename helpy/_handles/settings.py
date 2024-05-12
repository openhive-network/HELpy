from __future__ import annotations

from pathlib import Path

from pydantic import Field

from helpy._communication.abc.communicator import AbstractCommunicator  # noqa: TCH001
from helpy._communication.httpx_communicator import HttpxCommunicator
from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.url import HttpUrl  # noqa: TCH001


class HandleSettings(CommunicationSettings):
    http_endpoint: HttpUrl
    communicator: type[AbstractCommunicator] | AbstractCommunicator = HttpxCommunicator
    working_directory: Path = Field(default_factory=lambda: Path("."))
