from __future__ import annotations

from typing import TYPE_CHECKING

from hive_transfer_protocol.__private.handles.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from hive_transfer_protocol.__private.handles.beekeeper.api.async_api import BeekeeperApi as BeekeeperAsyncApi
from hive_transfer_protocol.__private.handles.beekeeper.api.sync_api import BeekeeperApi as BeekeeperSyncApi

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle


class BeekeeperAsyncApiCollection(AbstractAsyncApiCollection):
    def __init__(self, owner: AbstractAsyncHandle) -> None:
        super().__init__(owner)
        self.beekeeper = BeekeeperAsyncApi(owner=self._owner)


class BeekeeperSyncApiCollection(AbstractSyncApiCollection):
    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)
        self.beekeeper = BeekeeperSyncApi(owner=self._owner)
