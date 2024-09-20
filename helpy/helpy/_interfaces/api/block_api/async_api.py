from __future__ import annotations

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import block_api  # noqa: TCH001


class BlockApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_block_header(self, *, block_num: int) -> block_api.GetBlockHeader:
        raise NotImplementedError

    @api
    async def get_block(self, *, block_num: int) -> block_api.GetBlock:
        raise NotImplementedError

    @api
    async def get_block_range(self, starting_block_num: int, count: int) -> block_api.GetBlockRange:
        raise NotImplementedError
