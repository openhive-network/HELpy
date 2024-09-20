from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helpy._handles.beekeeper.api.session_holder import AsyncSessionHolder, SyncSessionHolder
    from helpy._interfaces.api.abc import ApiArgumentsToSerialize


def sync_apply_session_token(owner: SyncSessionHolder, arguments: ApiArgumentsToSerialize) -> ApiArgumentsToSerialize:
    arguments[1]["token"] = arguments[1].get("token") or owner.session.token
    return arguments


async def async_apply_session_token(
    owner: AsyncSessionHolder, arguments: ApiArgumentsToSerialize
) -> ApiArgumentsToSerialize:
    arguments[1]["token"] = arguments[1].get("token") or (await owner.session).token
    return arguments
