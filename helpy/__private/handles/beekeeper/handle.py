from __future__ import annotations

from typing import cast

from helpy.__private.handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from helpy.__private.handles.beekeeper.api.api_collection import (
    BeekeeperAsyncApiCollection,
    BeekeeperSyncApiCollection,
)


class Beekeeper(AbstractSyncHandle):
    """Synchronous handle for beekeeper service communication."""

    def _clone(self) -> Beekeeper:
        return Beekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperSyncApiCollection:
        return BeekeeperSyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperSyncApiCollection:
        return cast(BeekeeperSyncApiCollection, super().api)


class AsyncBeekeeper(AbstractAsyncHandle):
    """Asynchronous handle for beekeeper service communication."""

    def _clone(self) -> AsyncBeekeeper:
        return AsyncBeekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperAsyncApiCollection:
        return BeekeeperAsyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperAsyncApiCollection:
        return cast(BeekeeperAsyncApiCollection, super().api)
