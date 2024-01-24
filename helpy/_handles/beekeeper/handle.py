from __future__ import annotations

from typing import cast

from helpy._handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from helpy._handles.beekeeper.api.api_collection import (
    BeekeeperAsyncApiCollection,
    BeekeeperSyncApiCollection,
)

_handle_target_service_name = "beekeeper"


class Beekeeper(AbstractSyncHandle):
    """Synchronous handle for beekeeper service communication."""

    def _clone(self) -> Beekeeper:
        return Beekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperSyncApiCollection:  # type: ignore[override]
        return BeekeeperSyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperSyncApiCollection:  # type: ignore[override]
        return cast(BeekeeperSyncApiCollection, super().api)

    def _target_service(self) -> str:
        return _handle_target_service_name


class AsyncBeekeeper(AbstractAsyncHandle):
    """Asynchronous handle for beekeeper service communication."""

    def _clone(self) -> AsyncBeekeeper:
        return AsyncBeekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperAsyncApiCollection:  # type: ignore[override]
        return BeekeeperAsyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperAsyncApiCollection:  # type: ignore[override]
        return cast(BeekeeperAsyncApiCollection, super().api)

    def _target_service(self) -> str:
        return _handle_target_service_name
