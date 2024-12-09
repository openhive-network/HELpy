from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._handle.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from beekeepy._handle.beekeeper_handler.api import AsyncBeekeeperApi, SyncBeekeeperApi

if TYPE_CHECKING:
    from beekeepy._handle.beekeeper_handler.handle import (
        AsyncBeekeeper,
        Beekeeper,
        _AsyncSessionBatchHandle,
        _SyncSessionBatchHandle,
    )


class BeekeeperAsyncApiCollection(AbstractAsyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: AsyncBeekeeper | _AsyncSessionBatchHandle

    def __init__(self, owner: AsyncBeekeeper | _AsyncSessionBatchHandle) -> None:
        super().__init__(owner)
        self.beekeeper = AsyncBeekeeperApi(owner=self._owner)


class BeekeeperSyncApiCollection(AbstractSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: Beekeeper | _SyncSessionBatchHandle

    def __init__(self, owner: Beekeeper | _SyncSessionBatchHandle) -> None:
        super().__init__(owner)
        self.beekeeper = SyncBeekeeperApi(owner=self._owner)
