from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from beekeepy._interface.abc.asynchronous.session import Password
from beekeepy._interface.abc.asynchronous.session import Session as SessionInterface
from beekeepy._interface.asynchronous.wallet import (
    UnlockedWallet,
    Wallet,
)
from beekeepy._interface.state_invalidator import StateInvalidator
from beekeepy._interface.validators import validate_digest, validate_public_keys, validate_timeout, validate_wallet_name
from beekeepy.exceptions import (
    InvalidWalletError,
    NoWalletWithSuchNameError,
    WalletWithSuchNameAlreadyExistsError,
)
from beekeepy.exceptions.common import UnknownDecisionPathError
from beekeepy.exceptions.detectable import NotExistingKeyError

if TYPE_CHECKING:
    from beekeepy._handle.beekeeper import AsyncRemoteBeekeeper as AsynchronousRemoteBeekeeperHandle
    from beekeepy._interface.abc.asynchronous.wallet import (
        UnlockedWallet as UnlockedWalletInterface,
    )
    from beekeepy._interface.abc.asynchronous.wallet import (
        Wallet as WalletInterface,
    )
    from beekeepy._interface.delay_guard import AsyncDelayGuard
    from schemas.apis.beekeeper_api import GetInfo
    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature


class Session(SessionInterface, StateInvalidator):
    def __init__(
        self,
        *args: Any,
        beekeeper: AsynchronousRemoteBeekeeperHandle,
        guard: AsyncDelayGuard,
        use_session_token: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__beekeeper = beekeeper
        self.__session_token = use_session_token or ""
        self.__guard = guard

    async def get_info(self) -> GetInfo:
        return await self.__beekeeper.api.get_info(token=await self.token)

    async def create_wallet(  # type: ignore[override]
        self, *, name: str, password: str | None = None
    ) -> UnlockedWalletInterface | tuple[UnlockedWalletInterface, Password]:
        validate_wallet_name(wallet_name=name)
        with WalletWithSuchNameAlreadyExistsError(wallet_name=name), InvalidWalletError(wallet_name=name):
            create_result = await self.__beekeeper.api.create(
                wallet_name=name, password=password, token=await self.token
            )
        wallet = await self.__construct_unlocked_wallet(name)
        return wallet if password is not None else (wallet, create_result.password)

    async def open_wallet(self, *, name: str) -> WalletInterface:
        validate_wallet_name(wallet_name=name)
        with NoWalletWithSuchNameError(name):
            await self.__beekeeper.api.open(wallet_name=name, token=await self.token)
        return await self.__construct_wallet(name=name)

    async def close_session(self) -> None:
        if self.__beekeeper.is_session_token_set():
            await self.__beekeeper.api.close_session(token=await self.token)
            self.invalidate()

    async def lock_all(self) -> list[WalletInterface]:
        await self.__beekeeper.api.lock_all(token=await self.token)
        return await self.wallets

    async def set_timeout(self, seconds: int) -> None:
        validate_timeout(time=seconds)
        await self.__beekeeper.api.set_timeout(seconds=seconds, token=await self.token)

    async def sign_digest(self, *, sig_digest: str, key: str) -> Signature:
        validate_public_keys(key=key)
        validate_digest(sig_digest=sig_digest)
        with NotExistingKeyError(public_key=key):
            return (
                await self.__beekeeper.api.sign_digest(sig_digest=sig_digest, public_key=key, token=await self.token)
            ).signature
        raise UnknownDecisionPathError

    @property
    async def public_keys(self) -> list[PublicKey]:
        return [item.public_key for item in (await self.__beekeeper.api.get_public_keys(token=await self.token)).keys]

    @property
    async def wallets_unlocked(self) -> list[UnlockedWalletInterface]:
        result = []
        for wallet in await self.wallets:
            unlocked_wallet = await wallet.unlocked
            if unlocked_wallet:
                result.append(unlocked_wallet)
        return result

    @property
    async def token(self) -> str:
        if self.__session_token == "":
            self.__session_token = (await self.__beekeeper.api.create_session()).token
        return self.__session_token

    @property
    async def wallets(self) -> list[WalletInterface]:
        return await asyncio.gather(
            *[
                self.__construct_wallet(name=wallet.name)
                for wallet in (await self.__beekeeper.api.list_wallets(token=await self.token)).wallets
            ]
        )

    @property
    async def wallets_created(self) -> list[WalletInterface]:
        return await asyncio.gather(
            *[
                self.__construct_wallet(name=wallet.name)
                for wallet in (await self.__beekeeper.api.list_created_wallets(token=await self.token)).wallets
            ]
        )

    async def __construct_unlocked_wallet(self, name: str) -> UnlockedWallet:
        wallet = UnlockedWallet(
            name=name, beekeeper=self.__beekeeper, session_token=await self.token, guard=self.__guard
        )
        self.register_invalidable(wallet)
        return wallet

    async def __construct_wallet(self, name: str) -> WalletInterface:
        wallet = Wallet(name=name, beekeeper=self.__beekeeper, session_token=await self.token, guard=self.__guard)
        self.register_invalidable(wallet)
        return wallet
