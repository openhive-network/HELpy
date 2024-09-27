from __future__ import annotations

from datetime import timedelta
from os import environ
from typing import TYPE_CHECKING, Any, ClassVar, cast

from pydantic import BaseModel, Field

from helpy._interfaces.url import Url

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self


def _default_factory(env_name: str, default_factory: Callable[[str | None], Any]) -> Any:
    env_value = environ.get(env_name)
    return Field(default_factory=lambda: default_factory(env_value))


class CommunicationSettings(BaseModel):
    DEFAULT_TIMEOUT: ClassVar[timedelta] = timedelta(seconds=5)

    max_retries: int = _default_factory("HELPY_COMMUNICATION_MAX_RETRIES", lambda x: int(x or 5))
    """Amount of retries when sending request to service."""

    timeout: timedelta = _default_factory(
        "HELPY_COMMUNICATION_TIMEOUT_SECS",
        lambda x: (CommunicationSettings.DEFAULT_TIMEOUT if x is None else timedelta(seconds=int(x))),
    )
    """Maximum time for request to finish."""

    period_between_retries: timedelta = _default_factory(
        "HELPY_COMMUNICATION_PERIOD_BETWEEN_RETRIES_SECS", lambda x: timedelta(seconds=int(x or 1))
    )
    """Period between failed request and next retry."""

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
