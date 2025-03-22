from __future__ import annotations

from beekeepy._remote_handle.abc.batch_handle import ApiFactory, AsyncBatchHandle, SyncBatchHandle
from beekeepy._remote_handle.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from beekeepy._remote_handle.app_status_probe import AppStatusProbe
from beekeepy._remote_handle.beekeeper import AsyncBeekeeper as AsyncBeekeeperTemplate
from beekeepy._remote_handle.beekeeper import Beekeeper as BeekeeperTemplate
from beekeepy._remote_handle.beekeeper import _AsyncSessionBatchHandle as AsyncBeekeeprBatchHandle
from beekeepy._remote_handle.beekeeper import _SyncSessionBatchHandle as SyncBeekeeprBatchHandle
from beekeepy._remote_handle.settings import RemoteHandleSettings

AsyncBeekeeper = AsyncBeekeeperTemplate[RemoteHandleSettings]
Beekeeper = BeekeeperTemplate[RemoteHandleSettings]

__all__ = [
    "AbstractAsyncHandle",
    "AbstractSyncHandle",
    "ApiFactory",
    "AppStatusProbe",
    "AsyncBatchHandle",
    "AsyncBeekeeper",
    "AsyncBeekeeperTemplate",
    "AsyncBeekeeprBatchHandle",
    "Beekeeper",
    "BeekeeperTemplate",
    "RemoteHandleSettings",
    "SyncBatchHandle",
    "SyncBatchHandle",
    "SyncBeekeeprBatchHandle",
]
