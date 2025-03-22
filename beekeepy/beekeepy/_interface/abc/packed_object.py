from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from beekeepy._interface.settings import InterfaceSettings
from beekeepy._utilities.settings_holder import UniqueSettingsHolder

if TYPE_CHECKING:
    from beekeepy._communication import HttpUrl
    from beekeepy._interface.abc.asynchronous.beekeeper import (
        Beekeeper as AsynchronousBeekeeperInterface,
    )
    from beekeepy._interface.abc.synchronous.beekeeper import (
        Beekeeper as SynchronousBeekeeperInterface,
    )

__all__ = [
    "PackedSyncBeekeeper",
    "PackedAsyncBeekeeper",
]


class _SyncRemoteFactoryCallable(Protocol):
    def __call__(self, *, url_or_settings: HttpUrl | InterfaceSettings) -> SynchronousBeekeeperInterface: ...


class _AsyncRemoteFactoryCallable(Protocol):
    async def __call__(self, *, url_or_settings: HttpUrl | InterfaceSettings) -> AsynchronousBeekeeperInterface: ...


FactoryT = TypeVar("FactoryT", bound=_SyncRemoteFactoryCallable | _AsyncRemoteFactoryCallable)


class Packed(UniqueSettingsHolder[InterfaceSettings], Generic[FactoryT]):
    """Allows to transfer beekeeper handle to other process."""

    def __init__(self, settings: InterfaceSettings, unpack_factory: FactoryT) -> None:
        super().__init__(settings=settings)
        self._unpack_factory = unpack_factory


class PackedSyncBeekeeper(Packed[_SyncRemoteFactoryCallable]):
    def unpack(self) -> SynchronousBeekeeperInterface:
        return self._unpack_factory(url_or_settings=self.settings)


class PackedAsyncBeekeeper(Packed[_AsyncRemoteFactoryCallable]):
    async def unpack(self) -> AsynchronousBeekeeperInterface:
        return await self._unpack_factory(url_or_settings=self.settings)
