from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beekeepy._remote_handle.abc.api import ApiArgumentsToSerialize
    from beekeepy._remote_handle.api.session_holder import AsyncSessionHolder, SyncSessionHolder


def sync_apply_session_token(owner: SyncSessionHolder, arguments: ApiArgumentsToSerialize) -> ApiArgumentsToSerialize:
    arguments[1]["token"] = arguments[1].get("token") or owner.session.token
    return arguments


async def async_apply_session_token(
    owner: AsyncSessionHolder, arguments: ApiArgumentsToSerialize
) -> ApiArgumentsToSerialize:
    arguments[1]["token"] = arguments[1].get("token") or (await owner.session).token
    return arguments
