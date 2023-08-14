from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from hive_transfer_protocol.__private.interfaces.asset.asset import Hf26Asset  # noqa: TCH001
from schemas.__private.hive_fields_custom_schemas import Price  # noqa: TCH001
from schemas.debug_node_api import response_schemas as debug_node_api  # noqa: TCH001


class DebugNodeApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def debug_push_blocks(
        self, *, src_filename: str, count: int, skip_validate_invariants: bool = False
    ) -> debug_node_api.DebugPushBlocks:
        raise NotImplementedError

    @api
    def debug_generate_blocks(
        self, *, debug_key: str, count: int = 0, skip: int = 0, miss_blocks: int = 0, edit_if_needed: bool = True
    ) -> debug_node_api.DebugGenerateBlocks:
        raise NotImplementedError

    @api
    def debug_generate_blocks_until(
        self, *, debug_key: str, head_block_time: datetime, generate_sparsely: bool = True
    ) -> debug_node_api.DebugGenerateBlocksUntil:
        raise NotImplementedError

    @api
    def debug_get_head_block(self) -> debug_node_api.DebugGetHeadBlock:
        raise NotImplementedError

    @api
    def debug_get_witness_schedule(self) -> debug_node_api.DebugGetWitnessSchedule:
        raise NotImplementedError

    @api
    def debug_get_future_witness_schedule(self) -> debug_node_api.DebugGetWitnessSchedule:
        raise NotImplementedError

    @api
    def debug_get_hardfork_property_object(self) -> debug_node_api.DebugGetHardforkPropertyObject:
        raise NotImplementedError

    @api
    def debug_set_hardfork(self, *, hardfork_id: int) -> debug_node_api.DebugSetHardfork:
        raise NotImplementedError

    @api
    def debug_has_hardfork(self, *, hardfork_id: int) -> debug_node_api.DebugHasHardfork:
        raise NotImplementedError

    @api
    def debug_set_vest_pric(self, *, price: Price[Hf26Asset.Hive, Hf26Asset.Hbd]) -> debug_node_api.DebugSetVestPrice:
        raise NotImplementedError

    @api
    def debug_get_json_schema(self) -> debug_node_api.DebugGetJsonSchema:
        raise NotImplementedError

    @api
    def debug_throw_exception(self, throw_exception: bool = False) -> debug_node_api.DebugThrowException:
        raise NotImplementedError
