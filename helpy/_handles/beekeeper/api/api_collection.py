from __future__ import annotations

from typing import TYPE_CHECKING

from helpy._handles.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from helpy._handles.beekeeper.api import AsyncBeekeeperApi, SyncBeekeeperApi

if TYPE_CHECKING:
    from helpy._handles.abc.api import AsyncHandleT, SyncHandleT


class BeekeeperAsyncApiCollection(AbstractAsyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    def __init__(self, owner: AsyncHandleT) -> None:
        super().__init__(owner)
        self.beekeeper = AsyncBeekeeperApi(owner=self._owner)


class BeekeeperSyncApiCollection(AbstractSyncApiCollection):
    """Beekeepers collection of available apis in async version."""

    def __init__(self, owner: SyncHandleT) -> None:
        super().__init__(owner)
        self.beekeeper = SyncBeekeeperApi(owner=self._owner)
