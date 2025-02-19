from __future__ import annotations

from inspect import iscoroutinefunction, signature
from typing import TYPE_CHECKING

import pytest

from beekeepy._remote_handle.api import AsyncBeekeeperApi, SyncBeekeeperApi
from helpy._handles.hived.api.account_by_key_api import (
    AsyncAccountByKeyApi,
    SyncAccountByKeyApi,
)
from helpy._handles.hived.api.account_history_api import (
    AsyncAccountHistoryApi,
    SyncAccountHistoryApi,
)
from helpy._handles.hived.api.block_api import AsyncBlockApi, SyncBlockApi
from helpy._handles.hived.api.condenser_api import AsyncCondenserApi, SyncCondenserApi
from helpy._handles.hived.api.database_api import AsyncDatabaseApi, SyncDatabaseApi
from helpy._handles.hived.api.debug_node_api import AsyncDebugNodeApi, SyncDebugNodeApi
from helpy._handles.hived.api.jsonrpc import AsyncJsonrpc, SyncJsonrpc
from helpy._handles.hived.api.market_history_api import (
    AsyncMarketHistoryApi,
    SyncMarketHistoryApi,
)
from helpy._handles.hived.api.network_broadcast_api import (
    AsyncNetworkBroadcastApi,
    SyncNetworkBroadcastApi,
)
from helpy._handles.hived.api.network_node_api import AsyncNetworkNodeApi, SyncNetworkNodeApi
from helpy._handles.hived.api.rc_api import AsyncRcApi, SyncRcApi
from helpy._handles.hived.api.reputation_api import AsyncReputationApi, SyncReputationApi
from helpy._handles.hived.api.transaction_status_api import (
    AsyncTransactionStatusApi,
    SyncTransactionStatusApi,
)
from helpy._handles.hived.api.wallet_bridge_api import (
    AsyncWalletBridgeApi,
    SyncWalletBridgeApi,
)

if TYPE_CHECKING:
    from beekeepy._remote_handle.abc.api import AbstractAsyncApi, AbstractSyncApi, RegisteredApisT


@pytest.mark.parametrize(
    ("async_api", "sync_api"),
    [
        (AsyncAccountByKeyApi, SyncAccountByKeyApi),
        (AsyncAccountHistoryApi, SyncAccountHistoryApi),
        (AsyncBeekeeperApi, SyncBeekeeperApi),
        (AsyncBlockApi, SyncBlockApi),
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

    for api_method in sync_api_methods:
        sync_method = getattr(sync_api, api_method)
        assert not iscoroutinefunction(sync_method)

        async_method = getattr(async_api, api_method)
        assert iscoroutinefunction(async_method)

        assert signature(sync_method) == signature(async_method), f"inconsistency in: {api_method}"
