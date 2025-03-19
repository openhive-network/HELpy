from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from beekeepy import AsyncBeekeeper, AsyncSession, AsyncUnlockedWallet


@dataclass
class BeekeepyService:
    wallet: AsyncUnlockedWallet
    session: AsyncSession
    beekeeper: AsyncBeekeeper


@asynccontextmanager
async def create_beekeeper_service(*, wallet_name: str, password: str) -> AsyncGenerator[BeekeepyService, None]:
    """
    Create a beekeepy service with a wallet, session and beekeeper instance.

    This context manager handle the creation of a wallet and session and running beekeeper instance.
    If you already have a wallet with the same name, it will unlock it.

    Args:
        wallet_name (str): The wallet to create/unlock name.
        password (str): The wallet to create/unlock password.
    """
    async with await AsyncBeekeeper.factory() as beekeeper, await beekeeper.create_session() as session:
        wallet = (
            await session.create_wallet(name=wallet_name, password=password)
            if wallet_name not in [w.name for w in await session.wallets_created]
            else await (await session.open_wallet(name=wallet_name)).unlock(password=password)
        )

        yield BeekeepyService(wallet=wallet, session=session, beekeeper=beekeeper)
