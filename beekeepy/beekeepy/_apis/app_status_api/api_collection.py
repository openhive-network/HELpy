from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._apis.abc.api_collection import AbstractAsyncApiCollection, AbstractSyncApiCollection

if TYPE_CHECKING:
    from beekeepy._apis.abc.sendable import AsyncSendable, SyncSendable


class AppStatusProbeSyncApiCollection(AbstractSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: SyncSendable

    def __init__(self, owner: SyncSendable) -> None:
        super().__init__(owner)
        from beekeepy._apis.app_status_api.sync_api import AppStatusApi as SyncAppStatusApi

        self.app_status = SyncAppStatusApi(owner=self._owner)
        self.app_status_api = self.app_status


class AppStatusProbeAsyncApiCollection(AbstractAsyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: AsyncSendable

    def __init__(self, owner: AsyncSendable) -> None:
        super().__init__(owner)
        from beekeepy._apis.app_status_api.async_api import AppStatusApi as AsyncAppStatusApi

        self.app_status = AsyncAppStatusApi(owner=self._owner)
        self.app_status_api = self.app_status
