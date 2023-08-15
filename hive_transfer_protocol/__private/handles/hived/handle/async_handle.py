from __future__ import annotations

from typing import TYPE_CHECKING, cast

from hive_transfer_protocol.__private.handles.abc.handle import AbstractAsyncHandle
from hive_transfer_protocol.__private.handles.hived.api.api_collection import (
    HivedAsyncApiCollection,
)
from hive_transfer_protocol.__private.handles.hived.handle.common_helpers import HiveHandleCommonHelpers

if TYPE_CHECKING:
    from datetime import datetime

    from schemas.__private.hive_fields_basic_schemas import AccountName


class AsyncHived(AbstractAsyncHandle, HiveHandleCommonHelpers):
    def _clone(self) -> AsyncHived:
        return AsyncHived(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> HivedAsyncApiCollection:
        return HivedAsyncApiCollection(owner=self)

    @property
    def api(self) -> HivedAsyncApiCollection:
        return cast(HivedAsyncApiCollection, super().api)

    async def get_dynamic_global_properties(self) -> HiveHandleCommonHelpers.GetDynamicGlobalPropertiesT:
        return await self.api.database.get_dynamic_global_properties()

    async def get_last_block_number(self) -> int:
        return self._get_last_block_number(await self.get_dynamic_global_properties())

    async def get_last_irreversible_block_number(self) -> int:
        return self._get_last_irreversible_block_number(await self.get_dynamic_global_properties())

    async def get_head_block_time(self) -> datetime:
        return self._get_head_block_time(await self.get_dynamic_global_properties())

    async def get_current_witness(self) -> AccountName:
        return self._get_current_witness(await self.get_dynamic_global_properties())
