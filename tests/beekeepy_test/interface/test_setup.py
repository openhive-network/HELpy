from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy import Beekeeper
from beekeepy.exceptions import InvalidatedStateByClosingBeekeeperError, InvalidatedStateByClosingSessionError

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsFactory


def test_closing_with_delete(settings: SettingsFactory) -> None:
    # ARRANGE
    bk = Beekeeper.factory(settings=settings())

    # ACT & ASSERT (no throw)
    bk.teardown()
    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        bk.create_session()


def test_closing_with_with(settings: SettingsFactory) -> None:
    # ARRANGE, ACT & ASSERT (no throw)
    with Beekeeper.factory(settings=settings()) as bk, bk.create_session() as session:
        pass
    with pytest.raises(InvalidatedStateByClosingSessionError):
        session.wallets  # noqa: B018  # part of test


def test_session_tokens(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as bk:  # noqa: SIM117
        # ACT
        with bk.create_session() as s1, bk.create_session() as s2:
            # ASSERT
            assert s1.token != s2.token, "Tokens are not unique"
