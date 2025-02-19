from __future__ import annotations

from typing import Generic

from beekeepy._remote_handle.abc.api import AsyncHandleT, HandleT, SyncHandleT


class AbstractApiCollection(Generic[HandleT]):
    """Base class for Api Collections."""

    def __init__(self, owner: HandleT) -> None:
        self._owner = owner


class AbstractAsyncApiCollection(AbstractApiCollection[AsyncHandleT]):
    """Base class for Async Api Collections."""

    def __init__(self, owner: AsyncHandleT) -> None:
        super().__init__(owner)


class AbstractSyncApiCollection(AbstractApiCollection[SyncHandleT]):
    """Base class for Sync Api Collections."""

    def __init__(self, owner: SyncHandleT) -> None:
        super().__init__(owner)
