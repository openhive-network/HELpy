from __future__ import annotations

from typing import TYPE_CHECKING

from hive_transfer_protocol.__private.handles.beekeeper.api.async_api import BeekeeperApi as AsyncBeekeeperApi
from hive_transfer_protocol.__private.handles.beekeeper.api.sync_api import BeekeeperApi as SyncBeekeeperApi

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.api import RegisteredApisT


def test_is_beekeeper_api_consistent(registered_apis: RegisteredApisT) -> None:
    sync_api_methods = registered_apis[True][SyncBeekeeperApi._api_name()]
    async_api_methods = registered_apis[False][AsyncBeekeeperApi._api_name()]
    assert len(sync_api_methods) > 0
    assert len(async_api_methods) > 0
    assert sync_api_methods == async_api_methods
