from __future__ import annotations

from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from schemas.block_api import response_schemas as blocks_api  # noqa: TCH001


class BlocksApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def get_block_header(self, *, block_num: int) -> blocks_api.GetBlockHeader:
        raise NotImplementedError

    @api
    def get_block(self, *, block_num: int) -> blocks_api.GetBlock:
        raise NotImplementedError

    @api
    def get_block_range(self, starting_block_num: int, count: int) -> blocks_api.GetBlockRange:
        raise NotImplementedError
