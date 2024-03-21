from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel, Field

from helpy._interfaces.url import Url

if TYPE_CHECKING:
    from typing_extensions import Self


class CommunicationSettings(BaseModel):
    max_retries: int = 5
    timeout: timedelta = Field(default_factory=lambda: timedelta(seconds=5))
    period_between_retries: timedelta = Field(default_factory=lambda: timedelta(seconds=1))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {  # noqa: RUF012
            Url: lambda v: cast(Url, v).as_string()  # type: ignore[type-arg]
        }

    def export_settings(self) -> str:
        return self.json()

    @classmethod
    def import_settings(cls, settings: str) -> Self:
        return cls.parse_raw(settings)
