from __future__ import annotations

from typing import cast

from hive_transfer_protocol.__private.handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from hive_transfer_protocol.__private.handles.hived.api.api_collection import (
    HivedAsyncApiCollection,
    HivedSyncApiCollection,
)


class Hived(AbstractSyncHandle):
    def _clone(self) -> Hived:
        return Hived(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> HivedSyncApiCollection:
        return HivedSyncApiCollection(owner=self)

    @property
    def api(self) -> HivedSyncApiCollection:
        return cast(HivedSyncApiCollection, super().api)


class AsyncHived(AbstractAsyncHandle):
    def _clone(self) -> AsyncHived:
        return AsyncHived(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> HivedAsyncApiCollection:
        return HivedAsyncApiCollection(owner=self)

    @property
    def api(self) -> HivedAsyncApiCollection:
        return cast(HivedAsyncApiCollection, super().api)
