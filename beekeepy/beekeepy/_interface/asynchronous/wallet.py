from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._interface.abc.asynchronous.wallet import (
    UnlockedWallet as UnlockedWalletInterface,
)
from beekeepy._interface.abc.asynchronous.wallet import (
    Wallet as WalletInterface,
)
from beekeepy._interface.settings import InterfaceSettings
from beekeepy._interface.validators import validate_digest, validate_private_keys, validate_public_keys
from beekeepy._interface.wallets_common import WalletCommons
from beekeepy._remote_handle.async_beekeeper import AsyncBeekeeper as AsyncRemoteBeekeeper
from beekeepy._runnable_handle.callbacks_protocol import AsyncWalletLocked
from beekeepy._utilities.delay_guard import AsyncDelayGuard
from beekeepy.exceptions import (
    InvalidPasswordError,
    InvalidPrivateKeyError,
    InvalidPublicKeyError,
    MissingSTMPrefixError,
    NotExistingKeyError,
    UnknownDecisionPathError,
)

if TYPE_CHECKING:
    from datetime import datetime

    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature


class Wallet(
    WalletCommons[AsyncRemoteBeekeeper[InterfaceSettings], AsyncWalletLocked, AsyncDelayGuard], WalletInterface
):
    @property
    async def public_keys(self) -> list[PublicKey]:
        return [
            key.public_key
            for key in (await self._beekeeper.api.get_public_keys(wallet_name=self.name, token=self.session_token)).keys
        ]

    @property
    async def unlocked(self) -> UnlockedWallet | None:
        if await self.is_unlocked():
            return self.__construct_unlocked_wallet()
        return None

    async def unlock(self, password: str) -> UnlockedWallet:
        if not (await self.is_unlocked()):
            first_try = True
            while first_try or self._guard.error_occured():
                first_try = False
                async with self._guard:
                    with InvalidPasswordError(wallet_name=self.name):
                        await self._beekeeper.api.unlock(
                            wallet_name=self.name, password=password, token=self.session_token
                        )
        return self.__construct_unlocked_wallet()

    async def is_unlocked(self) -> bool:
        return self._is_wallet_unlocked(
            wallet_name=self.name,
            wallets=(await self._beekeeper.api.list_wallets(token=self.session_token)).wallets,
        )

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
    async def import_key(self, *, private_key: str) -> PublicKey:
        validate_private_keys(private_key=private_key)
        with InvalidPrivateKeyError(wifs=private_key):
            return (
                await self._beekeeper.api.import_key(
                    wallet_name=self.name, wif_key=private_key, token=self.session_token
                )
            ).public_key
        raise UnknownDecisionPathError

    @wallet_unlocked
    async def import_keys(self, *, private_keys: list[str]) -> list[PublicKey]:
        validate_private_keys(**{f"private_key_{i}": private_key for i, private_key in enumerate(private_keys)})

        with InvalidPrivateKeyError(wifs=private_keys):
            return (
                await self._beekeeper.api.import_keys(
                    wallet_name=self.name,
                    wif_keys=private_keys,
                    token=self.session_token,
                )
            ).public_keys
        raise UnknownDecisionPathError

    @wallet_unlocked
    async def remove_key(self, *, key: str) -> None:
        validate_public_keys(key=key)
        with NotExistingKeyError(public_key=key), MissingSTMPrefixError(public_key=key), InvalidPublicKeyError(
            public_keys=key
        ):
            await self._beekeeper.api.remove_key(wallet_name=self.name, public_key=key, token=self.session_token)

    @wallet_unlocked
    async def lock(self) -> None:
        await self._beekeeper.api.lock(wallet_name=self.name, token=self.session_token)

    @wallet_unlocked
    async def sign_digest(self, *, sig_digest: str, key: str) -> Signature:
        validate_public_keys(key=key)
        validate_digest(sig_digest=sig_digest)
        with MissingSTMPrefixError(public_key=key), InvalidPublicKeyError(public_keys=key), NotExistingKeyError(
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

    @wallet_unlocked
    async def encrypt_data(self, *, from_key: PublicKey, to_key: PublicKey, content: str, nonce: int = 0) -> str:
        validate_public_keys(from_key=from_key, to_key=to_key)
        with MissingSTMPrefixError(public_key=from_key), MissingSTMPrefixError(
            public_key=to_key
        ), InvalidPublicKeyError(public_keys=[from_key, to_key]), NotExistingKeyError(
            public_key=from_key, wallet_name=self.name
        ), NotExistingKeyError(public_key=to_key, wallet_name=self.name):
            return (
                await self._beekeeper.api.encrypt_data(
                    wallet_name=self.name,
                    from_public_key=from_key,
                    to_public_key=to_key,
                    content=content,
                    nonce=nonce,
                    token=self.session_token,
                )
            ).encrypted_content
        raise UnknownDecisionPathError

    @wallet_unlocked
    async def decrypt_data(self, *, from_key: PublicKey, to_key: PublicKey, content: str) -> str:
        validate_public_keys(from_key=from_key, to_key=to_key)
        with MissingSTMPrefixError(public_key=from_key), MissingSTMPrefixError(
            public_key=to_key
        ), InvalidPublicKeyError(public_keys=[from_key, to_key]), NotExistingKeyError(
            public_key=from_key, wallet_name=self.name
        ), NotExistingKeyError(public_key=to_key, wallet_name=self.name):
            return (
                await self._beekeeper.api.decrypt_data(
                    wallet_name=self.name,
                    from_public_key=from_key,
                    to_public_key=to_key,
                    encrypted_content=content,
                    token=self.session_token,
                )
            ).decrypted_content
        raise UnknownDecisionPathError

    async def _aenter(self) -> UnlockedWalletInterface:
        return self

    async def _afinally(self) -> None:
        await self.lock()
