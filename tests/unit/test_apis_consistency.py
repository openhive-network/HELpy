from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from hive_transfer_protocol.__private.handles.beekeeper.api import AsyncBeekeeperApi, SyncBeekeeperApi

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi, AbstractSyncApi, RegisteredApisT


@pytest.mark.parametrize(
    ("async_api", "sync_api"),
    [
        (AsyncBeekeeperApi, SyncBeekeeperApi),
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
