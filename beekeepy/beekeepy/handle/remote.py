from __future__ import annotations

from typing import TYPE_CHECKING

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

else:
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        # Translations
        **aggregate_same_import(
            "AsyncBeekeeperApi",
            "SyncBeekeeperApi",
            "BeekeeperSyncApiCollection",
            "BeekeeperAsyncApiCollection",
            module="beekeepy._apis.beekeeper_api",
        ),
        **aggregate_same_import(
            "AbstractAsyncApi",
            "AbstractSyncApi",
            "ApiArgumentSerialization",
            "RegisteredApisT",
            module="beekeepy._apis.abc.api",
        ),
        **aggregate_same_import(
            "AbstractSyncHandle",
            "AbstractAsyncHandle",
            "RemoteSettingsT",
            module="beekeepy._remote_handle.abc.handle",
        ),
        **aggregate_same_import(
            "AsyncSendable",
            "SyncSendable",
            module="beekeepy._apis.abc.sendable",
        ),
        AbstractAsyncApiCollection="beekeepy._apis.abc.api_collection",
        AbstractSyncApiCollection="beekeepy._apis.abc.api_collection",
        AppStatusProbeAsyncApiCollection="beekeepy._apis.app_status_api",
        AppStatusProbeSyncApiCollection="beekeepy._apis.app_status_api",
        AsyncBatchHandle="beekeepy._remote_handle.abc.batch_handle",
        AsyncBeekeeper="beekeepy._remote_handle._async_additional_definition",
        AsyncBeekeeperTemplate="beekeepy._remote_handle.async_beekeeper",
        Beekeeper="beekeepy._remote_handle._sync_additional_definition",
        RemoteHandleSettings="beekeepy._remote_handle.settings",
        SyncBatchHandle="beekeepy._remote_handle.abc.batch_handle",
        SyncBeekeeperTemplate="beekeepy._remote_handle.sync_beekeeper",
    )
