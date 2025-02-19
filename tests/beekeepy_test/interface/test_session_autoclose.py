from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy import AsyncBeekeeper, AsyncSession, Beekeeper, Session
from beekeepy.exceptions import InvalidatedStateError

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsFactory


def test_session_autoclose_after_beekeeper_teardown(settings: SettingsFactory) -> None:
    sessions: list[Session] = []
    with Beekeeper.factory(settings=settings()) as bk_parent, bk_parent.create_session() as ss_parent:
        with bk_parent.pack().unpack() as bk_child:
            sessions = [bk_child.create_session() for _ in range(10)]

        for session in sessions:
            with pytest.raises(InvalidatedStateError):
                session.get_info()

        ss_parent.get_info()  # NO ERROR

    with pytest.raises(InvalidatedStateError):
        ss_parent.get_info()


async def test_async_session_autoclose_after_beekeeper_teardown(settings: SettingsFactory) -> None:
    sessions: list[AsyncSession] = []
    async with await AsyncBeekeeper.factory(
        settings=settings()
    ) as bk_parent, await bk_parent.create_session() as ss_parent:
        async with await bk_parent.pack().unpack() as bk_child:
            sessions = [(await bk_child.create_session()) for _ in range(10)]

        for session in sessions:
            with pytest.raises(InvalidatedStateError):
                await session.get_info()

        await ss_parent.get_info()  # NO ERROR

    with pytest.raises(InvalidatedStateError):
        await ss_parent.get_info()
