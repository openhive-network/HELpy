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
from hive_transfer_protocol.__private.handles.hived.api.blocks_api import AsyncBlocksApi, SyncBlocksApi
from hive_transfer_protocol.__private.handles.hived.api.condenser_api import AsyncCondenserApi, SyncCondenserApi
from hive_transfer_protocol.__private.handles.hived.api.database_api import AsyncDatabaseApi, SyncDatabaseApi
from hive_transfer_protocol.__private.handles.hived.api.jsonrpc import AsyncJsonrpc, SyncJsonrpc
from hive_transfer_protocol.__private.handles.hived.api.market_history_api import (
    AsyncMarketHistoryApi,
    SyncMarketHistoryApi,
)
from hive_transfer_protocol.__private.handles.hived.api.network_broadcast_api import (
    AsyncNetworkBroadcastApi,
    SyncNetworkBroadcastApi,
)
from hive_transfer_protocol.__private.handles.hived.api.network_node_api import AsyncNetworkNodeApi, SyncNetworkNodeApi
from hive_transfer_protocol.__private.handles.hived.api.rc_api import AsyncRcApi, SyncRcApi
from hive_transfer_protocol.__private.handles.hived.api.reputation_api import AsyncReputationApi, SyncReputationApi
from hive_transfer_protocol.__private.handles.hived.api.transaction_status_api import (
    AsyncTransactionStatusApi,
    SyncTransactionStatusApi,
)
from hive_transfer_protocol.__private.handles.hived.api.wallet_bridge_api import (
    AsyncWalletBridgeApi,
    SyncWalletBridgeApi,
)

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
        self.transaction_status = AsyncTransactionStatusApi(owner=self._owner)
        self.network_node = AsyncNetworkNodeApi(owner=self._owner)
        self.jsonrpc = AsyncJsonrpc(owner=self._owner)
        self.condenser = AsyncCondenserApi(owner=self._owner)
        self.wallet_bridge = AsyncWalletBridgeApi(owner=self._owner)
        self.market_history = AsyncMarketHistoryApi(owner=self._owner)
        self.blocks_api = AsyncBlocksApi(owner=self._owner)


class HivedSyncApiCollection(AbstractSyncApiCollection):
    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)
        self.database = SyncDatabaseApi(owner=self._owner)
        self.account_history = SyncAccountHistoryApi(owner=self._owner)
        self.network_broadcast = SyncNetworkBroadcastApi(owner=self._owner)
        self.rc = SyncRcApi(owner=self._owner)
        self.reputation = SyncReputationApi(owner=self._owner)
        self.account_by_key = SyncAccountByKeyApi(owner=self._owner)
        self.transaction_status = SyncTransactionStatusApi(owner=self._owner)
        self.network_node = SyncNetworkNodeApi(owner=self._owner)
        self.jsonrpc = SyncJsonrpc(owner=self._owner)
        self.condenser = SyncCondenserApi(owner=self._owner)
        self.wallet_bridge = SyncWalletBridgeApi(owner=self._owner)
        self.market_history = SyncMarketHistoryApi(owner=self._owner)
        self.blocks_api = SyncBlocksApi(owner=self._owner)
