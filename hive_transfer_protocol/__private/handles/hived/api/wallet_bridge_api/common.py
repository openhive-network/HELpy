from __future__ import annotations

import json
from typing import Any, ClassVar, TypeAlias

from hive_transfer_protocol.__private.handles.hived.api.condenser_api.common import CondenserApiCommons
from hive_transfer_protocol.__private.handles.hived.api.database_api.common import DatabaseApiCommons


class WalletBridgeApiCommons:
    SORT_TYPES: ClassVar[TypeAlias] = DatabaseApiCommons.SORT_TYPES
    SORT_DIRECTION: ClassVar[TypeAlias] = DatabaseApiCommons.SORT_DIRECTION
    PROPOSAL_STATUS: ClassVar[TypeAlias] = DatabaseApiCommons.PROPOSAL_STATUS
    WITHDRAW_ROUTE_TYPES: ClassVar[TypeAlias] = CondenserApiCommons.WITHDRAW_ROUTE_TYPES

    @classmethod
    def _legacy_serialization(cls, args: list[Any]) -> str:
        return json.dumps(args)
