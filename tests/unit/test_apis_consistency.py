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
from hive_transfer_protocol.__private.handles.hived.api.database_api import AsyncDatabaseApi, SyncDatabaseApi
from hive_transfer_protocol.__private.handles.hived.api.network_broadcast_api import (
    AsyncNetworkBroadcastApi,
    SyncNetworkBroadcastApi,
)
from hive_transfer_protocol.__private.handles.hived.api.rc_api import AsyncRcApi, SyncRcApi
from hive_transfer_protocol.__private.handles.hived.api.reputation_api import AsyncReputationApi, SyncReputationApi
from hive_transfer_protocol.__private.handles.hived.api.transaction_status_api import (
    AsyncTransactionStatusApi,
    SyncTransactionStatusApi,
)

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi, AbstractSyncApi, RegisteredApisT


@pytest.mark.parametrize(
    ("async_api", "sync_api"),
    [
        (AsyncBeekeeperApi, SyncBeekeeperApi),
        (AsyncDatabaseApi, SyncDatabaseApi),
        (AsyncAccountHistoryApi, SyncAccountHistoryApi),
        (AsyncNetworkBroadcastApi, SyncNetworkBroadcastApi),
        (AsyncRcApi, SyncRcApi),
        (AsyncReputationApi, SyncReputationApi),
        (AsyncAccountByKeyApi, SyncAccountByKeyApi),
        (AsyncTransactionStatusApi, SyncTransactionStatusApi),
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
