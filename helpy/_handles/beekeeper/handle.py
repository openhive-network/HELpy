from __future__ import annotations

from typing import cast

from helpy._handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from helpy._handles.batch_handle import AsyncBatchHandle, SyncBatchHandle
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

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[BeekeeperSyncApiCollection]:
        return SyncBatchHandle(
            url=self.http_endpoint,
            communicator=self._communicator,
            api=lambda o: BeekeeperSyncApiCollection(o),
            delay_error_on_data_access=delay_error_on_data_access,
        )


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

    def batch(self, *, delay_error_on_data_access: bool = False) -> AsyncBatchHandle[BeekeeperAsyncApiCollection]:
        return AsyncBatchHandle(
            url=self.http_endpoint,
            communicator=self._communicator,
            api=lambda o: BeekeeperAsyncApiCollection(o),
            delay_error_on_data_access=delay_error_on_data_access,
        )
