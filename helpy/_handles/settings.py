from __future__ import annotations

from pathlib import Path

from pydantic import Field, validator

from helpy._communication.abc.communicator import AbstractCommunicator  # noqa: TCH001
from helpy._communication.httpx_communicator import HttpxCommunicator
from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.url import HttpUrl


class HandleSettings(CommunicationSettings):
    notification_endpoint: HttpUrl | None = None  # if set to None, address will be set automatically
    http_endpoint: HttpUrl | None = None  # if set to None, address will be set automatically
    communicator: type[AbstractCommunicator] | AbstractCommunicator = HttpxCommunicator
    working_directory: Path = Field(default_factory=lambda: Path("."))

    @validator("notification_endpoint", "http_endpoint", pre=True)
    def _convert(cls, v: str | None) -> HttpUrl | None:  # noqa: N805
        return HttpUrl(v) if v is not None else None
