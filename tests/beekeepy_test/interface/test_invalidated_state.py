from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import pytest
from local_tools.beekeepy.generators import generate_wallet_name, generate_wallet_password

from beekeepy import Beekeeper
from beekeepy.exceptions import InvalidatedStateByClosingBeekeeperError, InvalidatedStateByClosingSessionError

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsFactory

    from beekeepy import Session, Wallet


@pytest.fixture
def beekeepy_interfaces(settings: SettingsFactory) -> Iterator[tuple[Beekeeper, Session, Wallet]]:
    bk = Beekeeper.factory(settings=settings())
    session = bk.create_session()
    wallet = session.create_wallet(name=generate_wallet_name(), password=generate_wallet_password())
    yield (bk, session, wallet)
    bk.teardown()


def test_invalidated_by_closing_beekeeper(beekeepy_interfaces: tuple[Beekeeper, Session, Wallet]) -> None:
    # ARRANGE
    bk, session, wallet = beekeepy_interfaces

    # ACT
    bk.teardown()

    # ASSERT
    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        bk.session  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        session.public_keys  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        wallet.name  # noqa: B018


def test_invalidated_by_closing_session(beekeepy_interfaces: tuple[Beekeeper, Session, Wallet]) -> None:
    # ARRANGE
    bk, session, wallet = beekeepy_interfaces

    # ACT
    session.close_session()

    # ASSERT
    bk.session  # NO RAISE  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingSessionError):
        session.public_keys  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingSessionError):
        wallet.name  # noqa: B018


def test_multiple_teardown(beekeepy_interfaces: tuple[Beekeeper, Session, Wallet]) -> None:
    # ARRANGE
    bk, session, wallet = beekeepy_interfaces

    # ACT
    bk.teardown()

    # ASSERT
    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        bk.session  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        session.public_keys  # noqa: B018

    with pytest.raises(InvalidatedStateByClosingBeekeeperError):
        wallet.name  # noqa: B018

    bk.teardown()  # NO RAISE
