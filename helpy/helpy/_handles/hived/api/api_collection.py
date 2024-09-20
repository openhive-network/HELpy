from __future__ import annotations

from typing import TYPE_CHECKING

from helpy._interfaces.api.abc import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from helpy._interfaces.api.account_by_key_api import (
    AsyncAccountByKeyApi,
    SyncAccountByKeyApi,
)
from helpy._interfaces.api.account_history_api import (
    AsyncAccountHistoryApi,
    SyncAccountHistoryApi,
)
from helpy._interfaces.api.block_api import AsyncBlockApi, SyncBlockApi
from helpy._interfaces.api.condenser_api import AsyncCondenserApi, SyncCondenserApi
from helpy._interfaces.api.database_api import AsyncDatabaseApi, SyncDatabaseApi
from helpy._interfaces.api.debug_node_api import AsyncDebugNodeApi, SyncDebugNodeApi
from helpy._interfaces.api.jsonrpc import AsyncJsonrpc, SyncJsonrpc
from helpy._interfaces.api.market_history_api import (
    AsyncMarketHistoryApi,
    SyncMarketHistoryApi,
)
from helpy._interfaces.api.network_broadcast_api import (
    AsyncNetworkBroadcastApi,
    SyncNetworkBroadcastApi,
)
from helpy._interfaces.api.network_node_api import AsyncNetworkNodeApi, SyncNetworkNodeApi
from helpy._interfaces.api.rc_api import AsyncRcApi, SyncRcApi
from helpy._interfaces.api.reputation_api import AsyncReputationApi, SyncReputationApi
from helpy._interfaces.api.transaction_status_api import (
    AsyncTransactionStatusApi,
    SyncTransactionStatusApi,
)
from helpy._interfaces.api.wallet_bridge_api import (
    AsyncWalletBridgeApi,
    SyncWalletBridgeApi,
)

if TYPE_CHECKING:
    from helpy._interfaces.api.abc import AsyncHandleT, SyncHandleT


class HivedAsyncApiCollection(AbstractAsyncApiCollection):
    def __init__(self, owner: AsyncHandleT) -> None:
        super().__init__(owner)
        self.account_by_key = AsyncAccountByKeyApi(owner=self._owner)
        self.account_history = AsyncAccountHistoryApi(owner=self._owner)
        self.block = AsyncBlockApi(owner=self._owner)
        self.condenser = AsyncCondenserApi(owner=self._owner)
        self.database = AsyncDatabaseApi(owner=self._owner)
        self.debug_node = AsyncDebugNodeApi(owner=self._owner)
        self.jsonrpc = AsyncJsonrpc(owner=self._owner)
        self.market_history = AsyncMarketHistoryApi(owner=self._owner)
        self.network_broadcast = AsyncNetworkBroadcastApi(owner=self._owner)
        self.network_node = AsyncNetworkNodeApi(owner=self._owner)
        self.rc = AsyncRcApi(owner=self._owner)
        self.reputation = AsyncReputationApi(owner=self._owner)
        self.transaction_status = AsyncTransactionStatusApi(owner=self._owner)
        self.wallet_bridge = AsyncWalletBridgeApi(owner=self._owner)


class HivedSyncApiCollection(AbstractSyncApiCollection):
    def __init__(self, owner: SyncHandleT) -> None:
        super().__init__(owner)
        self.account_by_key = SyncAccountByKeyApi(owner=self._owner)
        self.account_history = SyncAccountHistoryApi(owner=self._owner)
        self.block = SyncBlockApi(owner=self._owner)
        self.condenser = SyncCondenserApi(owner=self._owner)
        self.database = SyncDatabaseApi(owner=self._owner)
        self.debug_node = SyncDebugNodeApi(owner=self._owner)
        self.jsonrpc = SyncJsonrpc(owner=self._owner)
        self.market_history = SyncMarketHistoryApi(owner=self._owner)
        self.network_broadcast = SyncNetworkBroadcastApi(owner=self._owner)
        self.network_node = SyncNetworkNodeApi(owner=self._owner)
        self.rc = SyncRcApi(owner=self._owner)
        self.reputation = SyncReputationApi(owner=self._owner)
        self.transaction_status = SyncTransactionStatusApi(owner=self._owner)
        self.wallet_bridge = SyncWalletBridgeApi(owner=self._owner)
