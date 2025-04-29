from __future__ import annotations

from typing import TYPE_CHECKING, cast

from beekeepy._remote_handle.abc.api import ApiArgumentsToSerialize, SyncHandleT
from beekeepy._remote_handle.api.apply_session_token import sync_apply_session_token
from beekeepy._remote_handle.api.beekeeper_api_commons import BeekeeperApiCommons
from beekeepy._remote_handle.api.session_holder import SyncSessionHolder
from beekeepy._remote_handle.api.sync_api_generated import BeekeeperApi as BaseBeekeeperApi

if TYPE_CHECKING:
    from beekeepy._remote_handle.beekeeper import Beekeeper, _SyncSessionBatchHandle


class BeekeeperApi(BaseBeekeeperApi, BeekeeperApiCommons[SyncHandleT]):  # type: ignore[misc]
    _owner: Beekeeper | _SyncSessionBatchHandle

    def __init__(self, owner: Beekeeper | _SyncSessionBatchHandle) -> None:
        self._verify_is_owner_can_hold_session_token(owner=owner)
        super().__init__(owner=owner)

    def _additional_arguments_actions(
        self, endpoint_name: str, arguments: ApiArgumentsToSerialize
    ) -> ApiArgumentsToSerialize:
        if not self._token_required(endpoint_name):
            return super()._additional_arguments_actions(endpoint_name, arguments)
        return sync_apply_session_token(cast(SyncSessionHolder, self._owner), arguments)

    def _get_requires_session_holder_type(self) -> type[SyncSessionHolder]:
        return SyncSessionHolder  # type: ignore[no-any-return]
