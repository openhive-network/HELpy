from __future__ import annotations

from typing import TYPE_CHECKING, cast

from hive_transfer_protocol.__private.handles.abc.handle import AbstractSyncHandle
from hive_transfer_protocol.__private.handles.hived.api.api_collection import (
    HivedSyncApiCollection,
)
from hive_transfer_protocol.__private.handles.hived.handle.common_helpers import HiveHandleCommonHelpers

if TYPE_CHECKING:
    from datetime import datetime

    from schemas.__private.hive_fields_basic_schemas import AccountName


class Hived(AbstractSyncHandle, HiveHandleCommonHelpers):
    def _clone(self) -> Hived:
        return Hived(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> HivedSyncApiCollection:
        return HivedSyncApiCollection(owner=self)

    @property
    def api(self) -> HivedSyncApiCollection:
        return cast(HivedSyncApiCollection, super().api)

    def get_dynamic_global_properties(self) -> HiveHandleCommonHelpers.GetDynamicGlobalPropertiesT:
        return self.api.database.get_dynamic_global_properties()

    def get_last_block_number(self) -> int:
        return self._get_last_block_number(self.get_dynamic_global_properties())

    def get_last_irreversible_block_number(self) -> int:
        return self._get_last_irreversible_block_number(self.get_dynamic_global_properties())

    def get_head_block_time(self) -> datetime:
        return self._get_head_block_time(self.get_dynamic_global_properties())

    def get_current_witness(self) -> AccountName:
        return self._get_current_witness(self.get_dynamic_global_properties())
