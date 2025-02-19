from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy import Beekeeper

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsFactory


def test_closing_with_delete(settings: SettingsFactory) -> None:
    # ARRANGE
    sets = settings()
    bk = Beekeeper.factory(settings=sets)

    # ACT & ASSERT (no throw)
    bk.teardown()
    assert not (sets.ensured_working_directory / "beekeeper.pid").exists()


def test_closing_with_with(settings: SettingsFactory) -> None:
    # ARRANGE, ACT & ASSERT (no throw)
    sets = settings()
    with Beekeeper.factory(settings=sets):
        assert (sets.ensured_working_directory / "beekeeper.pid").exists()


def test_session_tokens(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as bk:  # noqa: SIM117
        # ACT
        with bk.create_session() as s1, bk.create_session() as s2:
            # ASSERT
            assert s1.token != s2.token, "Tokens are not unique"
