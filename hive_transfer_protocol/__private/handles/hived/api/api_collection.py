from __future__ import annotations

from typing import TYPE_CHECKING

from hive_transfer_protocol.__private.handles.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from hive_transfer_protocol.__private.handles.hived.api.account_by_key_api import (
    AsyncAccountByKeyApi,
    SyncAccountByKeyApi,
)
from hive_transfer_protocol.__private.handles.hived.api.account_history_api import (
    AsyncAccountHistoryApi,
    SyncAccountHistoryApi,
)
from hive_transfer_protocol.__private.handles.hived.api.database_api import AsyncDatabaseApi, SyncDatabaseApi
from hive_transfer_protocol.__private.handles.hived.api.network_broadcast_api import (
    AsyncNetworkBroadcastApi,
    SyncNetworkBroadcastApi,
)
from hive_transfer_protocol.__private.handles.hived.api.rc_api import AsyncRcApi, SyncRcApi
from hive_transfer_protocol.__private.handles.hived.api.reputation_api import AsyncReputationApi, SyncReputationApi

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle


class HivedAsyncApiCollection(AbstractAsyncApiCollection):
    def __init__(self, owner: AbstractAsyncHandle) -> None:
        super().__init__(owner)
        self.database = AsyncDatabaseApi(owner=self._owner)
        self.account_history = AsyncAccountHistoryApi(owner=self._owner)
        self.network_broadcast = AsyncNetworkBroadcastApi(owner=self._owner)
        self.rc = AsyncRcApi(owner=self._owner)
        self.reputation = AsyncReputationApi(owner=self._owner)
        self.account_by_key = AsyncAccountByKeyApi(owner=self._owner)


class HivedSyncApiCollection(AbstractSyncApiCollection):
    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)
        self.database = SyncDatabaseApi(owner=self._owner)
        self.account_history = SyncAccountHistoryApi(owner=self._owner)
        self.network_broadcast = SyncNetworkBroadcastApi(owner=self._owner)
        self.rc = SyncRcApi(owner=self._owner)
        self.reputation = SyncReputationApi(owner=self._owner)
        self.account_by_key = SyncAccountByKeyApi(owner=self._owner)
