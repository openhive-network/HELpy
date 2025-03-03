from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy import Beekeeper

if TYPE_CHECKING:
    from typing import Iterator

    from local_tools.beekeepy.models import SettingsFactory

    from beekeepy import Session, UnlockedWallet, Wallet


@pytest.fixture()
def beekeeper(settings: SettingsFactory) -> Iterator[Beekeeper]:
    with Beekeeper.factory(settings=settings()) as bk:
        yield bk


@pytest.fixture()
def session(beekeeper: Beekeeper) -> Iterator[Session]:
    with beekeeper.create_session() as ss:
        yield ss


@pytest.fixture()
def wallet(session: Session) -> Wallet:
    with session.create_wallet(name="wallet", password="wallet"):  # noqa: S106
        pass

    return session.open_wallet(name="wallet")


@pytest.fixture()
def unlocked_wallet(wallet: Wallet) -> Iterator[UnlockedWallet]:
    with wallet.unlock(password="wallet") as uw:  # noqa: S106
        yield uw
