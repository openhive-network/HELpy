from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [
    "AbstractAsyncApi",
    "AbstractAsyncApiCollection",
    "AbstractAsyncHandle",
    "AbstractSyncApi",
    "AbstractSyncApiCollection",
    "AbstractSyncHandle",
    "ApiArgumentSerialization",
    "AppStatusProbeAsyncApiCollection",
    "AppStatusProbeSyncApiCollection",
    "AsyncBatchHandle",
    "AsyncBeekeeper",
    "AsyncBeekeeperApi",
    "AsyncBeekeeperTemplate",
    "AsyncSendable",
    "Beekeeper",
    "BeekeeperAsyncApiCollection",
    "BeekeeperSyncApiCollection",
    "RegisteredApisT",
    "RemoteHandleSettings",
    "RemoteSettingsT",
    "SyncBatchHandle",
    "SyncBeekeeperApi",
    "SyncBeekeeperTemplate",
    "SyncSendable",
]

if TYPE_CHECKING:
    from beekeepy._apis.abc.api import AbstractAsyncApi, AbstractSyncApi, ApiArgumentSerialization, RegisteredApisT
    from beekeepy._apis.abc.api_collection import (
        AbstractAsyncApiCollection,
        AbstractSyncApiCollection,
    )
    from beekeepy._apis.abc.sendable import (
        AsyncSendable,
        SyncSendable,
    )
    from beekeepy._apis.app_status_api import (
        AppStatusProbeAsyncApiCollection,
        AppStatusProbeSyncApiCollection,
    )
    from beekeepy._apis.beekeeper_api import (
        AsyncBeekeeperApi,
        BeekeeperAsyncApiCollection,
        BeekeeperSyncApiCollection,
        SyncBeekeeperApi,
    )
    from beekeepy._remote_handle._async_additional_definition import AsyncBeekeeper
    from beekeepy._remote_handle._sync_additional_definition import Beekeeper
    from beekeepy._remote_handle.abc.batch_handle import AsyncBatchHandle, SyncBatchHandle
    from beekeepy._remote_handle.abc.handle import AbstractAsyncHandle, AbstractSyncHandle, RemoteSettingsT
    from beekeepy._remote_handle.async_beekeeper import AsyncBeekeeperTemplate
    from beekeepy._remote_handle.settings import RemoteHandleSettings
    from beekeepy._remote_handle.sync_beekeeper import SyncBeekeeperTemplate


__getattr__ = lazy_module_factory(
    globals(),
    # Translations
    *aggregate_same_import(
        "AsyncBeekeeperApi",
        "SyncBeekeeperApi",
        "BeekeeperSyncApiCollection",
        "BeekeeperAsyncApiCollection",
        module="beekeepy._apis.beekeeper_api",
    ),
    *aggregate_same_import(
        "AbstractAsyncApi",
        "AbstractSyncApi",
        "ApiArgumentSerialization",
        "RegisteredApisT",
        module="beekeepy._apis.abc.api",
    ),
    *aggregate_same_import(
        "AbstractSyncHandle",
        "AbstractAsyncHandle",
        "RemoteSettingsT",
        module="beekeepy._remote_handle.abc.handle",
    ),
    *aggregate_same_import(
        "AsyncSendable",
        "SyncSendable",
        module="beekeepy._apis.abc.sendable",
    ),
    ("beekeepy._apis.abc.api_collection", "AbstractAsyncApiCollection"),
    ("beekeepy._apis.abc.api_collection", "AbstractSyncApiCollection"),
    ("beekeepy._apis.app_status_api", "AppStatusProbeAsyncApiCollection"),
    ("beekeepy._apis.app_status_api", "AppStatusProbeSyncApiCollection"),
    ("beekeepy._remote_handle.abc.batch_handle", "AsyncBatchHandle"),
    ("beekeepy._remote_handle._async_additional_definition", "AsyncBeekeeper"),
    ("beekeepy._remote_handle.async_beekeeper", "AsyncBeekeeperTemplate"),
    ("beekeepy._remote_handle._sync_additional_definition", "Beekeeper"),
    ("beekeepy._remote_handle.settings", "RemoteHandleSettings"),
    ("beekeepy._remote_handle.abc.batch_handle", "SyncBatchHandle"),
    ("beekeepy._remote_handle.sync_beekeeper", "SyncBeekeeperTemplate"),
)
