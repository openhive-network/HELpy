from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._remote_handle.abc.api import ApiArgumentsToSerialize, AsyncHandleT
from beekeepy._remote_handle.api.apply_session_token import async_apply_session_token
from beekeepy._remote_handle.api.async_api_generated import BeekeeperApi as BaseBeekeeperApi
from beekeepy._remote_handle.api.beekeeper_api_commons import BeekeeperApiCommons
from beekeepy._remote_handle.api.session_holder import AsyncSessionHolder

if TYPE_CHECKING:
    from beekeepy._remote_handle.beekeeper import AsyncBeekeeper, _AsyncSessionBatchHandle


class BeekeeperApi(BaseBeekeeperApi, BeekeeperApiCommons[AsyncHandleT]):  # type: ignore[misc]
    _owner: AsyncBeekeeper | _AsyncSessionBatchHandle

    def __init__(self, owner: AsyncBeekeeper | _AsyncSessionBatchHandle) -> None:
        self._verify_is_owner_can_hold_session_token(owner=owner)
        super().__init__(owner=owner)

    async def _additional_arguments_actions(
        self, endpoint_name: str, arguments: ApiArgumentsToSerialize
    ) -> ApiArgumentsToSerialize:
        if not self._token_required(endpoint_name):
            return await super()._additional_arguments_actions(endpoint_name, arguments)
        return await async_apply_session_token(self._owner, arguments)

    def _get_requires_session_holder_type(self) -> type[AsyncSessionHolder]:
        return AsyncSessionHolder  # type: ignore[no-any-return]
