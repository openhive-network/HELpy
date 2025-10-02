from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from beekeepy._communication.settings import CommunicationSettings
from beekeepy._interface.settings import InterfaceSettings
from beekeepy._utilities.context import ContextSync
from beekeepy._utilities.context_settings_updater import ContextSettingsUpdater

if TYPE_CHECKING:
    from beekeepy._communication.url import HttpUrl
    from beekeepy._interface.abc.packed_object import PackedSyncBeekeeper
    from beekeepy._interface.abc.synchronous.session import Session


class Beekeeper(ContextSync["Beekeeper"], ContextSettingsUpdater[CommunicationSettings], ABC):
    @abstractmethod
    def create_session(self, *, salt: str | None = None) -> Session: ...

    @property
    def settings(self) -> InterfaceSettings:
        """Returns read-only settings."""
        return cast(InterfaceSettings, self._get_copy_of_settings())

    @property
    def http_endpoint(self) -> HttpUrl:
        return self.settings.ensured_http_endpoint

    @property
    @abstractmethod
    def session(self) -> Session: ...

    @abstractmethod
    def teardown(self) -> None: ...

    @abstractmethod
    def pack(self) -> PackedSyncBeekeeper: ...

    @abstractmethod
    def detach(self) -> int:
        """Detaches process and returns PID."""

    @classmethod
    def factory(cls, *, settings: InterfaceSettings | None = None) -> Beekeeper:
        from beekeepy._interface.synchronous.beekeeper import Beekeeper as BeekeeperImplementation

        return BeekeeperImplementation._factory(settings=settings)

    @classmethod
    def remote_factory(cls, *, url_or_settings: InterfaceSettings | HttpUrl) -> Beekeeper:
        from beekeepy._interface.synchronous.beekeeper import Beekeeper as BeekeeperImplementation

        return BeekeeperImplementation._remote_factory(url_or_settings=url_or_settings)
