from __future__ import annotations

from typing import TYPE_CHECKING

from helpy._interfaces.asset.asset import Hf26Asset
from schemas.apis.database_api import GetDynamicGlobalProperties

if TYPE_CHECKING:
    from datetime import datetime
    from typing import TypeAlias

    from schemas.fields.basic import AccountName


class HiveHandleCommonHelpers:
    GetDynamicGlobalPropertiesT: TypeAlias = GetDynamicGlobalProperties[Hf26Asset.Hive, Hf26Asset.Hbd, Hf26Asset.Vests]

    def _get_last_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.head_block_number

    def _get_last_irreversible_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.last_irreversible_block_num

    def _get_head_block_time(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> datetime:
        return dynamic_global_properties.time

    def _get_current_witness(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> AccountName:
        return dynamic_global_properties.current_witness
