from __future__ import annotations

from typing import TYPE_CHECKING, cast

from helpy._handles.abc.handle import AbstractSyncHandle
from helpy._handles.app_status_probe.api_collection import AppStatusProbeSyncApiCollection
from helpy._handles.settings import Settings

if TYPE_CHECKING:
    from helpy._handles.batch_handle import SyncBatchHandle
    from helpy._interfaces.api.app_status_api import SyncAppStatusApi


class AppStatusProbe(AbstractSyncHandle[Settings]):
    """Synchronous handle for probing."""

    def _construct_api(self) -> AppStatusProbeSyncApiCollection:
        return AppStatusProbeSyncApiCollection(owner=self)

    @property
    def apis(self) -> AppStatusProbeSyncApiCollection:
        return cast(AppStatusProbeSyncApiCollection, super().api)

    @property
    def api(self) -> SyncAppStatusApi:  # type: ignore[override]
        return self.apis.app_status

    def _target_service(self) -> str:
        return "app_status_probe"

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[AppStatusProbeSyncApiCollection]:
        raise NotImplementedError
