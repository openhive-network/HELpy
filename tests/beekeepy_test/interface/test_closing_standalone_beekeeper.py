from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy import Beekeeper
from beekeepy.exceptions import (
    CommunicationError,
    FailedToDetectRunningBeekeeperError,
    UndistinguishableBeekeeperInstancesError,
)
from beekeepy.handle.runnable import close_already_running_beekeeper

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsFactory


def test_match_by_cwd(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as b1, Beekeeper.factory(settings=settings()) as b2, Beekeeper.factory(
        settings=settings()
    ) as b3:
        assert b1.settings.working_directory != b2.settings.working_directory != b3.settings.working_directory

        # ACT
        b2.detach()
        close_already_running_beekeeper(cwd=b2.settings.working_directory)

        # ASSERT
        b1.create_session()
        b3.create_session()

        with pytest.raises(CommunicationError):
            b2.create_session()


def test_match_by_port(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as b1, Beekeeper.factory(settings=settings()) as b2, Beekeeper.factory(
        settings=settings()
    ) as b3:
        # ACT
        close_already_running_beekeeper(port=b2.http_endpoint.port)

        # ASSERT
        b1.create_session()
        b3.create_session()

        with pytest.raises(CommunicationError):
            b2.create_session()


def test_match_fail_multiple_beekeepers(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as b1, Beekeeper.factory(settings=settings()) as b2, Beekeeper.factory(
        settings=settings()
    ) as b3:
        # ACT
        with pytest.raises(UndistinguishableBeekeeperInstancesError):
            close_already_running_beekeeper()

        # ASSERT
        for bk in [b1, b2, b3]:
            bk.create_session()


@pytest.mark.skip("Not sure how to run this test, as it kills beekeepers in other tests")
def test_match_multiple_beekeepers(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as b1, Beekeeper.factory(settings=settings()) as b2, Beekeeper.factory(
        settings=settings()
    ) as b3:
        # ACT
        close_already_running_beekeeper(on_multiple_match_kill_all=True)

        # ASSERT
        for bk in [b1, b2, b3]:
            with pytest.raises(CommunicationError):
                bk.create_session()


def test_no_match_fail(settings: SettingsFactory) -> None:
    # ARRANGE
    with Beekeeper.factory(settings=settings()) as b1, Beekeeper.factory(settings=settings()) as b2, Beekeeper.factory(
        settings=settings()
    ) as b3:
        # ACT
        with pytest.raises(FailedToDetectRunningBeekeeperError):
            close_already_running_beekeeper(port=2137)

        # ASSERT
        for bk in [b1, b2, b3]:
            bk.create_session()
