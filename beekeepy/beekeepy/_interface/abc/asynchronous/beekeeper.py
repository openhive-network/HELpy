from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from beekeepy._interface.settings import Settings
from helpy import ContextAsync, HttpUrl
from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.context_settings_updater import ContextSettingsUpdater

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous.session import Session
    from beekeepy._interface.abc.packed_object import PackedAsyncBeekeeper


class Beekeeper(ContextAsync["Beekeeper"], ContextSettingsUpdater[CommunicationSettings], ABC):
    @abstractmethod
    async def create_session(self, *, salt: str | None = None) -> Session: ...

    @property
    def settings(self) -> Settings:
        """Returns read-only settings."""
        return cast(Settings, self._get_copy_of_settings())

    @property
    @abstractmethod
    async def session(self) -> Session: ...

    @abstractmethod
    def teardown(self) -> None: ...

    @abstractmethod
    def pack(self) -> PackedAsyncBeekeeper: ...

    @abstractmethod
    def detach(self) -> int:
        """Detaches process and returns PID."""

    @classmethod
    async def factory(cls, *, settings: Settings | None = None) -> Beekeeper:
        from beekeepy._interface.asynchronous.beekeeper import Beekeeper as BeekeeperImplementation

        return await BeekeeperImplementation._factory(settings=settings)

    @classmethod
    async def remote_factory(cls, *, url_or_settings: Settings | HttpUrl) -> Beekeeper:
        from beekeepy._interface.asynchronous.beekeeper import Beekeeper as BeekeeperImplementation

        return await BeekeeperImplementation._remote_factory(url_or_settings=url_or_settings)
