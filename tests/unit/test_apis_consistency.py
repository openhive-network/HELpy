from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from hive_transfer_protocol.__private.handles.beekeeper.api import AsyncBeekeeperApi, SyncBeekeeperApi
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
from hive_transfer_protocol.__private.handles.hived.api.debug_node_api import AsyncDebugNodeApi, SyncDebugNodeApi
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
    from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi, AbstractSyncApi, RegisteredApisT


@pytest.mark.parametrize(
    ("async_api", "sync_api"),
    [
        (AsyncAccountByKeyApi, SyncAccountByKeyApi),
        (AsyncAccountHistoryApi, SyncAccountHistoryApi),
        (AsyncBeekeeperApi, SyncBeekeeperApi),
        (AsyncBlocksApi, SyncBlocksApi),
        (AsyncCondenserApi, SyncCondenserApi),
        (AsyncDatabaseApi, SyncDatabaseApi),
        (AsyncDebugNodeApi, SyncDebugNodeApi),
        (AsyncJsonrpc, SyncJsonrpc),
        (AsyncMarketHistoryApi, SyncMarketHistoryApi),
        (AsyncNetworkBroadcastApi, SyncNetworkBroadcastApi),
        (AsyncNetworkNodeApi, SyncNetworkNodeApi),
        (AsyncRcApi, SyncRcApi),
        (AsyncReputationApi, SyncReputationApi),
        (AsyncTransactionStatusApi, SyncTransactionStatusApi),
        (AsyncWalletBridgeApi, SyncWalletBridgeApi),
    ],
)
def test_is_api_consistent(
    registered_apis: RegisteredApisT, async_api: AbstractAsyncApi, sync_api: AbstractSyncApi
) -> None:
    sync_api_methods = registered_apis[True][sync_api._api_name()]
    async_api_methods = registered_apis[False][async_api._api_name()]
    assert len(sync_api_methods) > 0
    assert len(async_api_methods) > 0
    assert sync_api_methods == async_api_methods
