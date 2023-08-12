from __future__ import annotations

from typing import Generic

from hive_transfer_protocol.__private.handles.abc.api import HandleT
from hive_transfer_protocol.__private.handles.abc.handle import (
    AbstractAsyncHandle,
    AbstractSyncHandle,
)


class AbstractApiCollection(Generic[HandleT]):
    """Base class for Api Collections."""

    def __init__(self, owner: HandleT) -> None:
        self._owner = owner


class AbstractAsyncApiCollection(AbstractApiCollection[AbstractAsyncHandle]):
    """Base class for Async Api Collections."""

    def __init__(self, owner: AbstractAsyncHandle) -> None:
        super().__init__(owner)


class AbstractSyncApiCollection(AbstractApiCollection[AbstractSyncHandle]):
    """Base class for Sync Api Collections."""

    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)
