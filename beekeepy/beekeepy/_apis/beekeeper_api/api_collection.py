from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._apis.app_status_api import AppStatusProbeAsyncApiCollection, AppStatusProbeSyncApiCollection
from beekeepy._apis.beekeeper_api.async_api import BeekeeperApi as AsyncBeekeeperApi
from beekeepy._apis.beekeeper_api.sync_api import BeekeeperApi as SyncBeekeeperApi

if TYPE_CHECKING:
    from beekeepy._apis.abc.session_holder import AsyncSessionHolder, SyncSessionHolder


class BeekeeperAsyncApiCollection(AppStatusProbeAsyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: AsyncSessionHolder

    def __init__(self, owner: AsyncSessionHolder) -> None:
        super().__init__(owner)
        self.beekeeper = AsyncBeekeeperApi(owner=self._owner)
        self.beekeeper_api = self.beekeeper


class BeekeeperSyncApiCollection(AppStatusProbeSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    _owner: SyncSessionHolder

    def __init__(self, owner: SyncSessionHolder) -> None:
        super().__init__(owner)
        self.beekeeper = SyncBeekeeperApi(owner=self._owner)
        self.beekeeper_api = self.beekeeper
