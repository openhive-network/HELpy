from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from beekeepy._communication.settings import CommunicationSettings
from beekeepy._interface.context import ContextAsync
from beekeepy._interface.context_settings_updater import ContextSettingsUpdater
from beekeepy._runnable_handle.settings import Settings

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous.session import Session
    from beekeepy._interface.abc.packed_object import PackedAsyncBeekeeper
    from beekeepy._interface.url import HttpUrl


class Beekeeper(ContextAsync["Beekeeper"], ContextSettingsUpdater[CommunicationSettings], ABC):
    @abstractmethod
    async def create_session(self, *, salt: str | None = None) -> Session: ...

    @property
    def settings(self) -> Settings:
        """Returns read-only settings."""
        return cast(Settings, self._get_copy_of_settings())

    @property
    def http_endpoint(self) -> HttpUrl:
        return self.settings.ensured_http_endpoint

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
