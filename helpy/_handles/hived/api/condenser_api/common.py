from __future__ import annotations

from typing import Any, ClassVar, Literal, TypeAlias

from helpy._handles.abc.api import AbstractApi
from helpy._handles.hived.api.database_api.common import DatabaseApiCommons


class CondenserApiCommons:
    SORT_TYPES: ClassVar[TypeAlias] = DatabaseApiCommons.SORT_TYPES
    SORT_DIRECTION: ClassVar[TypeAlias] = DatabaseApiCommons.SORT_DIRECTION
    PROPOSAL_STATUS: ClassVar[TypeAlias] = DatabaseApiCommons.PROPOSAL_STATUS
    WITHDRAW_ROUTE_TYPES = Literal["incoming", "outgoing", "all"]

    @classmethod
    def _legacy_serialization(cls, args: list[Any]) -> str:
        return AbstractApi.json_dumps()(args)
