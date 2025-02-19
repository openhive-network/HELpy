from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from beekeepy._interface.settings_holder import UniqueSettingsHolder
from beekeepy._runnable_handle.settings import Settings

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous.beekeeper import (
        Beekeeper as AsynchronousBeekeeperInterface,
    )
    from beekeepy._interface.abc.synchronous.beekeeper import (
        Beekeeper as SynchronousBeekeeperInterface,
    )
    from beekeepy._interface.url import HttpUrl

__all__ = [
    "PackedSyncBeekeeper",
    "PackedAsyncBeekeeper",
]


class _SyncRemoteFactoryCallable(Protocol):
    def __call__(self, *, url_or_settings: HttpUrl | Settings) -> SynchronousBeekeeperInterface: ...


class _AsyncRemoteFactoryCallable(Protocol):
    async def __call__(self, *, url_or_settings: HttpUrl | Settings) -> AsynchronousBeekeeperInterface: ...


FactoryT = TypeVar("FactoryT", bound=_SyncRemoteFactoryCallable | _AsyncRemoteFactoryCallable)


class Packed(UniqueSettingsHolder[Settings], Generic[FactoryT]):
    """Allows to transfer beekeeper handle to other process."""

    def __init__(self, settings: Settings, unpack_factory: FactoryT) -> None:
        super().__init__(settings=settings)
        self._unpack_factory = unpack_factory
        self._prepare_settings_for_packing()

    def _prepare_settings_for_packing(self) -> None:
        with self.update_settings() as settings:
            settings.notification_endpoint = None


class PackedSyncBeekeeper(Packed[_SyncRemoteFactoryCallable]):
    def unpack(self) -> SynchronousBeekeeperInterface:
        return self._unpack_factory(url_or_settings=self.settings)


class PackedAsyncBeekeeper(Packed[_AsyncRemoteFactoryCallable]):
    async def unpack(self) -> AsynchronousBeekeeperInterface:
        return await self._unpack_factory(url_or_settings=self.settings)
