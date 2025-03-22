from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._apis import AppStatusProbeSyncApiCollection
from beekeepy._remote_handle.abc.handle import AbstractSyncHandle
from beekeepy._remote_handle.settings import RemoteHandleSettings

if TYPE_CHECKING:
    from beekeepy._apis import SyncAppStatusApi
    from beekeepy._remote_handle.abc.batch_handle import SyncBatchHandle


class AppStatusProbe(AbstractSyncHandle[RemoteHandleSettings, AppStatusProbeSyncApiCollection]):
    """Synchronous handle for probing."""

    def _construct_api(self) -> AppStatusProbeSyncApiCollection:
        return AppStatusProbeSyncApiCollection(owner=self)

    @property
    def api(self) -> SyncAppStatusApi:  # type: ignore[override]
        return self.apis.app_status

    def _target_service(self) -> str:
        return "app_status_probe"

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[AppStatusProbeSyncApiCollection]:
        raise NotImplementedError
