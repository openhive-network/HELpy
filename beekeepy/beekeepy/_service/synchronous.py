from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from beekeepy import Beekeeper, Session, UnlockedWallet


@dataclass
class BeekeepyService:
    wallet: UnlockedWallet
    session: Session
    beekeeper: Beekeeper


@contextmanager
def create_beekeepy_service(*, wallet_name: str, password: str) -> Generator[BeekeepyService, None, None]:
    """
    Create a beekeepy service with a wallet and session.

    This context manager handle the creation of a wallet and session and running beekeeper instance.
    If you already have a wallet with the same name, it will unlock it.

    Args:
        wallet_name (str): The wallet to create/unlock name.
        password (str): The wallet to create/unlock password.
    """
    with Beekeeper.factory() as beekeeper, beekeeper.create_session() as session:
        wallet = (
            session.create_wallet(name=wallet_name, password=password)
            if wallet_name not in [w.name for w in session.wallets_created]
            else (session.open_wallet(name=wallet_name)).unlock(password=password)
        )

        yield BeekeepyService(wallet=wallet, session=session, beekeeper=beekeeper)
