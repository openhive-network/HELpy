from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._handle.beekeeper import AsyncRemoteBeekeeper
from beekeepy._handle.callbacks_protocol import AsyncWalletLocked
from beekeepy._interface.abc.asynchronous.wallet import (
    UnlockedWallet as UnlockedWalletInterface,
)
from beekeepy._interface.abc.asynchronous.wallet import (
    Wallet as WalletInterface,
)
from beekeepy._interface.common import WalletCommons
from beekeepy._interface.delay_guard import AsyncDelayGuard
from beekeepy._interface.validators import validate_digest, validate_private_keys, validate_public_keys
from beekeepy.exceptions import (
    InvalidPasswordError,
    InvalidPrivateKeyError,
    InvalidPublicKeyError,
    MissingSTMPrefixError,
    NotExistingKeyError,
    UnknownDecisionPathError,
)
from helpy import wax

if TYPE_CHECKING:
    from datetime import datetime

    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature


class Wallet(WalletCommons[AsyncRemoteBeekeeper, AsyncWalletLocked, AsyncDelayGuard], WalletInterface):
    @property
    async def public_keys(self) -> list[PublicKey]:
        return [
            key.public_key
            for key in (await self._beekeeper.api.get_public_keys(wallet_name=self.name, token=self.session_token)).keys
        ]

    @property
    async def unlocked(self) -> UnlockedWallet | None:
        if await self.__is_unlocked():
            return self.__construct_unlocked_wallet()
        return None

    async def unlock(self, password: str) -> UnlockedWallet:
        if not (await self.__is_unlocked()):
            first_try = True
            while first_try or self._guard.error_occured():
                first_try = False
                async with self._guard:
                    with InvalidPasswordError(wallet_name=self.name):
                        await self._beekeeper.api.unlock(
                            wallet_name=self.name, password=password, token=self.session_token
                        )
        return self.__construct_unlocked_wallet()

    async def __is_unlocked(self) -> bool:
        for wallet in (await self._beekeeper.api.list_wallets(token=self.session_token)).wallets:
            if wallet.name == self.name:
                self._last_lock_state = wallet.unlocked
                return self._last_lock_state
        self._last_lock_state = False
        return self._last_lock_state

    def __construct_unlocked_wallet(self) -> UnlockedWallet:
        wallet = UnlockedWallet(
            name=self.name, beekeeper=self._beekeeper, session_token=self.session_token, guard=self._guard
        )
        wallet._last_lock_state = False
        self.register_invalidable(wallet)
        return wallet


class UnlockedWallet(Wallet, UnlockedWalletInterface):
    wallet_unlocked = WalletCommons.check_wallet

    @wallet_unlocked
    async def generate_key(self, *, salt: str | None = None) -> PublicKey:  # noqa: ARG002
        return await self.import_key(private_key=wax.generate_private_key())

    @wallet_unlocked
    async def import_key(self, *, private_key: str) -> PublicKey:
        validate_private_keys(private_key=private_key)
        with InvalidPrivateKeyError(wif=private_key):
            return (
                await self._beekeeper.api.import_key(
                    wallet_name=self.name, wif_key=private_key, token=self.session_token
                )
            ).public_key
        raise UnknownDecisionPathError

    @wallet_unlocked
    async def remove_key(self, *, key: str) -> None:
        validate_public_keys(key=key)
        with NotExistingKeyError(public_key=key), MissingSTMPrefixError(public_key=key), InvalidPublicKeyError(
            public_key=key
        ):
            await self._beekeeper.api.remove_key(wallet_name=self.name, public_key=key, token=self.session_token)

    @wallet_unlocked
    async def lock(self) -> None:
        await self._beekeeper.api.lock(wallet_name=self.name, token=self.session_token)

    @wallet_unlocked
    async def sign_digest(self, *, sig_digest: str, key: str) -> Signature:
        validate_public_keys(key=key)
        validate_digest(sig_digest=sig_digest)
        with MissingSTMPrefixError(public_key=key), InvalidPublicKeyError(public_key=key), NotExistingKeyError(
            public_key=key
        ):
            return (
                await self._beekeeper.api.sign_digest(
                    sig_digest=sig_digest, public_key=key, wallet_name=self.name, token=self.session_token
                )
            ).signature
        raise UnknownDecisionPathError

    @wallet_unlocked
    async def has_matching_private_key(self, *, key: str) -> bool:
        validate_public_keys(key=key)
        return (
            await self._beekeeper.api.has_matching_private_key(
                wallet_name=self.name, public_key=key, token=self.session_token
            )
        ).exists

    @property
    async def lock_time(self) -> datetime:
        return (await self._beekeeper.api.get_info(token=self.session_token)).timeout_time

    async def _aenter(self) -> UnlockedWalletInterface:
        return self

    async def _afinally(self) -> None:
        await self.lock()
