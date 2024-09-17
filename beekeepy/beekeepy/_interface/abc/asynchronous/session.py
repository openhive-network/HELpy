from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeAlias, overload

from helpy import ContextAsync

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous.wallet import UnlockedWallet, Wallet
    from schemas.apis.beekeeper_api import GetInfo
    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature

Password: TypeAlias = str


class Session(ContextAsync["Session"], ABC):
    @abstractmethod
    async def get_info(self) -> GetInfo: ...

    @overload
    @abstractmethod
    async def create_wallet(self, *, name: str, password: str) -> UnlockedWallet: ...

    @overload
    @abstractmethod
    async def create_wallet(self, *, name: str, password: None = None) -> tuple[UnlockedWallet, Password]: ...

    @abstractmethod
    async def create_wallet(
        self, *, name: str, password: str | None = None
    ) -> UnlockedWallet | tuple[UnlockedWallet, str]: ...

    @abstractmethod
    async def open_wallet(self, *, name: str) -> Wallet: ...

    @abstractmethod
    async def close_session(self) -> None: ...

    @abstractmethod
    async def lock_all(self) -> list[Wallet]: ...

    @abstractmethod
    async def set_timeout(self, seconds: int) -> None: ...

    @abstractmethod
    async def sign_digest(self, *, sig_digest: str, key: str) -> Signature: ...

    @property
    @abstractmethod
    async def wallets(self) -> list[Wallet]: ...

    @property
    @abstractmethod
    async def wallets_created(self) -> list[Wallet]: ...

    @property
    async def wallets_unlocked(self) -> list[UnlockedWallet]:
        result = []
        for wallet in await self.wallets:
            unlocked_wallet = await wallet.unlocked
            if unlocked_wallet:
                result.append(unlocked_wallet)
        return result

    @property
    @abstractmethod
    async def token(self) -> str: ...

    @property
    @abstractmethod
    async def public_keys(self) -> list[PublicKey]: ...

    async def _aenter(self) -> Session:
        return self

    async def _afinally(self) -> None:
        await self.close_session()
