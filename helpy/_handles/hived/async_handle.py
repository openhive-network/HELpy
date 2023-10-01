from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

from helpy._handles.abc.handle import AbstractAsyncHandle
from helpy._handles.hived.api.api_collection import (
    HivedAsyncApiCollection,
)
from helpy._handles.hived.common_helpers import HiveHandleCommonHelpers
from helpy._interfaces.time import Time
from helpy.exceptions import BlockWaitTimeoutError

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from schemas.fields.basic import AccountName


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

    async def wait_number_of_blocks(self, blocks_to_wait: int, *, timeout: float = math.inf) -> None:
        assert blocks_to_wait > 0
        await self.wait_for_block_with_number(await self.get_last_block_number() + blocks_to_wait, timeout=timeout)

    async def wait_for_block_with_number(self, block_number: int, *, timeout: float | timedelta = math.inf) -> None:
        async def __is_block_with_number_reached() -> bool:
            last = await self.get_last_block_number()
            return last >= block_number

        await Time.async_wait_for(
            __is_block_with_number_reached,
            timeout=timeout,
            timeout_error_message=f"Waiting too long for block {block_number}",
            poll_time=2.0,
        )

    async def wait_for_irreversible_block(
        self, number: int | None = None, *, max_blocks_to_wait: int | None = None, timeout: float | timedelta = math.inf
    ) -> None:
        last_block_number = await self.get_last_block_number()
        target_block_number = number or last_block_number
        max_wait_block_number = (last_block_number + max_blocks_to_wait) if max_blocks_to_wait is not None else None

        async def __is_block_with_number_irreversible() -> bool:
            if max_wait_block_number is not None:
                await self.__assert_block_with_number_reached_irreversibility_before_limit(
                    target_block_number, max_wait_block_number
                )

            last_irreversible_block_number = await self.get_last_irreversible_block_number()
            return last_irreversible_block_number >= target_block_number

        await Time.async_wait_for(
            __is_block_with_number_irreversible,
            timeout=timeout,
            timeout_error_message=f"Waiting too long for irreversible block {target_block_number}",
            poll_time=2.0,
        )

    async def __assert_block_with_number_reached_irreversibility_before_limit(
        self, block_number: int, max_wait_block_number: int
    ) -> None:
        response = await self.get_dynamic_global_properties()
        last_block_number = response.head_block_number
        last_irreversible_block_number = response.last_irreversible_block_num

        def __expected_block_was_reached_but_is_still_not_irreversible() -> bool:
            return last_block_number >= max_wait_block_number and last_irreversible_block_number < block_number

        if __expected_block_was_reached_but_is_still_not_irreversible():
            raise BlockWaitTimeoutError(last_block_number, block_number, last_irreversible_block_number)
