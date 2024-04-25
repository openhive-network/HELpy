from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from helpy._handles.beekeeper.api.session_holder import SessionHolder


def apply_session_token(
    owner: SessionHolder, args: list[Any], kwargs: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    assert len(args) == 0, "Unknown args format"
    kwargs["token"] = owner.session_token
    return ([], kwargs)
