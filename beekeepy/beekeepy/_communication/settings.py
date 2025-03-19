from __future__ import annotations

from datetime import timedelta
from os import environ
from typing import TYPE_CHECKING, Any, ClassVar, cast

from msgspec import field

from beekeepy._interface.url import Url
from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.decoders import get_hf26_decoder

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self


class CommunicationSettings(PreconfiguredBaseModel):
    class EnvironNames:
        TIMEOUT: ClassVar[str] = "HELPY_COMMUNICATION_MAX_RETRIES"
        PERIOD_BETWEEN_RETRIES: ClassVar[str] = "HELPY_COMMUNICATION_TIMEOUT_SECS"
        RETRIES: ClassVar[str] = "HELPY_COMMUNICATION_PERIOD_BETWEEN_RETRIES_SECS"

    class Defaults:
        TIMEOUT: ClassVar[timedelta] = timedelta(seconds=5)
        PERIOD_BETWEEN_RETRIES: ClassVar[timedelta] = timedelta(seconds=0.2)
        RETRIES: ClassVar[int] = 5

        @staticmethod
        def default_factory(env_name: str, default_factory: Callable[[str | None], Any]) -> Any:
            env_value = environ.get(env_name)
            return field(default_factory=lambda: default_factory(env_value))

    max_retries: int = Defaults.default_factory(
        EnvironNames.RETRIES,
        lambda x: (CommunicationSettings.Defaults.RETRIES if x is None else timedelta(seconds=int(x))),
    )
    """Amount of retries when sending request to service."""

    timeout: timedelta = Defaults.default_factory(
        EnvironNames.TIMEOUT,
        lambda x: (CommunicationSettings.Defaults.TIMEOUT if x is None else timedelta(seconds=int(x))),
    )
    """Maximum time for single request to finish."""

    period_between_retries: timedelta = Defaults.default_factory(
        EnvironNames.PERIOD_BETWEEN_RETRIES,
        lambda x: (CommunicationSettings.Defaults.PERIOD_BETWEEN_RETRIES if x is None else timedelta(seconds=int(x))),
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
        decoder = get_hf26_decoder(cls)
        return decoder.decode(settings)
