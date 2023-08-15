from __future__ import annotations

from typing import TYPE_CHECKING

from hive_transfer_protocol.__private.handles.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from hive_transfer_protocol.__private.handles.beekeeper.api import AsyncBeekeeperApi, SyncBeekeeperApi

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle


class BeekeeperAsyncApiCollection(AbstractAsyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    def __init__(self, owner: AbstractAsyncHandle) -> None:
        super().__init__(owner)
        self.beekeeper = AsyncBeekeeperApi(owner=self._owner)


class BeekeeperSyncApiCollection(AbstractSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)
        self.beekeeper = SyncBeekeeperApi(owner=self._owner)
