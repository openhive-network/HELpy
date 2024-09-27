from __future__ import annotations

from typing import TYPE_CHECKING

from helpy._interfaces.api.abc import (
    AbstractSyncApiCollection,
)
from helpy._interfaces.api.app_status_api import SyncAppStatusApi

if TYPE_CHECKING:
    from helpy._handles.app_status_probe.handle import AppStatusProbe


class AppStatusProbeSyncApiCollection(AbstractSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: AppStatusProbe

    def __init__(self, owner: AppStatusProbe) -> None:
        super().__init__(owner)
        self.app_status = SyncAppStatusApi(owner=self._owner)
