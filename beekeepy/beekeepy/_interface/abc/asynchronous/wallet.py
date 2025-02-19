from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from beekeepy._interface.context import ContextAsync
from beekeepy._interface.wallets_common import ContainsWalletName

if TYPE_CHECKING:
    from datetime import datetime

    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature


class Wallet(ContainsWalletName, ABC):
    @property
    @abstractmethod
    async def public_keys(self) -> list[PublicKey]: ...

    @property
    @abstractmethod
    async def unlocked(self) -> UnlockedWallet | None: ...

    @abstractmethod
    async def is_unlocked(self) -> bool: ...

    @abstractmethod
    async def unlock(self, password: str) -> UnlockedWallet: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class UnlockedWallet(Wallet, ContextAsync["UnlockedWallet"], ABC):
    @abstractmethod
    async def import_key(self, *, private_key: str) -> PublicKey: ...

    @abstractmethod
    async def import_keys(self, *, private_keys: list[str]) -> list[PublicKey]: ...

    @abstractmethod
    async def remove_key(self, *, key: str) -> None: ...

    @abstractmethod
    async def lock(self) -> None: ...

    @abstractmethod
    async def sign_digest(self, *, sig_digest: str, key: str) -> Signature: ...

    @abstractmethod
    async def has_matching_private_key(self, *, key: str) -> bool: ...

    @property
    @abstractmethod
    async def lock_time(self) -> datetime: ...

    @abstractmethod
    async def encrypt_data(self, *, from_key: PublicKey, to_key: PublicKey, content: str, nonce: int = 0) -> str: ...

    @abstractmethod
    async def decrypt_data(self, *, from_key: PublicKey, to_key: PublicKey, content: str) -> str: ...
