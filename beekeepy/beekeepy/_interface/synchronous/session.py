from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from beekeepy._interface.abc.synchronous.session import Password
from beekeepy._interface.abc.synchronous.session import Session as SessionInterface
from beekeepy._interface.synchronous.wallet import (
    UnlockedWallet,
    Wallet,
)
from beekeepy._interface.validators import validate_digest, validate_public_keys, validate_timeout
from beekeepy._utilities.state_invalidator import StateInvalidator
from beekeepy.exceptions import (
    InvalidatedStateByClosingSessionError,
    InvalidWalletError,
    NotExistingKeyError,
    NoWalletWithSuchNameError,
    UnknownDecisionPathError,
    WalletWithSuchNameAlreadyExistsError,
)

if TYPE_CHECKING:
    from beekeepy._interface.abc.synchronous.wallet import (
        UnlockedWallet as UnlockedWalletInterface,
    )
    from beekeepy._interface.abc.synchronous.wallet import (
        Wallet as WalletInterface,
    )
    from beekeepy._interface.settings import InterfaceSettings
    from beekeepy._remote_handle import BeekeeperTemplate as SyncRemoteBeekeeper
    from beekeepy._utilities.delay_guard import SyncDelayGuard
    from schemas.apis.beekeeper_api import GetInfo
    from schemas.fields.basic import PublicKey
    from schemas.fields.hex import Signature


class Session(SessionInterface, StateInvalidator):
    def __init__(
        self,
        *args: Any,
        beekeeper: SyncRemoteBeekeeper[InterfaceSettings],
        guard: SyncDelayGuard,
        use_session_token: str | None = None,
        default_session_close_callback: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__beekeeper = beekeeper
        self.__session_token = use_session_token or ""
        self.__guard = guard
        self.__default_session_close_callback = default_session_close_callback

    def get_info(self) -> GetInfo:
        return self.__beekeeper.api.get_info(token=self.token)

    def create_wallet(  # type: ignore[override]
        self, *, name: str, password: str | None = None
    ) -> UnlockedWalletInterface | tuple[UnlockedWalletInterface, Password]:
        with WalletWithSuchNameAlreadyExistsError(wallet_name=name), InvalidWalletError(wallet_name=name):
            create_result = self.__beekeeper.api.create(wallet_name=name, password=password, token=self.token)
        wallet = self.__construct_unlocked_wallet(name)
        return wallet if password is not None else (wallet, create_result.password)

    def open_wallet(self, *, name: str) -> WalletInterface:
        with NoWalletWithSuchNameError(name), InvalidWalletError(wallet_name=name):
            self.__beekeeper.api.open(wallet_name=name, token=self.token)
        return self.__construct_wallet(name=name)

    def close_session(self) -> None:
        if self.__session_token != "":
            self.__beekeeper.api.close_session(token=self.token)
            if self.__default_session_close_callback is not None:
                self.__default_session_close_callback()
            self.invalidate(InvalidatedStateByClosingSessionError())

    def lock_all(self) -> list[WalletInterface]:
        self.__beekeeper.api.lock_all(token=self.token)
        return self.wallets

    def set_timeout(self, seconds: int) -> None:
        validate_timeout(time=seconds)
        self.__beekeeper.api.set_timeout(seconds=seconds, token=self.token)

    def sign_digest(self, *, sig_digest: str, key: str) -> Signature:
        validate_public_keys(key=key)
        validate_digest(sig_digest=sig_digest)
        with NotExistingKeyError(public_key=key):
            return self.__beekeeper.api.sign_digest(sig_digest=sig_digest, public_key=key, token=self.token).signature
        raise UnknownDecisionPathError

    @property
    def wallets_unlocked(self) -> list[UnlockedWalletInterface]:
        return self.__list_unlocked_wallets()

    @property
    def token(self) -> str:
        if self.__session_token == "":
            self.__session_token = self.__beekeeper.api.create_session().token
        return self.__session_token

    @property
    def wallets(self) -> list[WalletInterface]:
        return self.__list_wallets()

    @property
    def wallets_created(self) -> list[WalletInterface]:
        return [
            self.__construct_wallet(name=wallet.name)
            for wallet in self.__beekeeper.api.list_created_wallets(token=self.token).wallets
        ]

    @property
    def public_keys(self) -> list[PublicKey]:
        return [key.public_key for key in self.__beekeeper.api.get_public_keys(token=self.token).keys]

    def __construct_unlocked_wallet(self, name: str) -> UnlockedWallet:
        wallet = UnlockedWallet(name=name, beekeeper=self.__beekeeper, session_token=self.token, guard=self.__guard)
        self.register_invalidable(wallet)
        return wallet

    def __construct_wallet(self, name: str) -> Wallet:
        wallet = Wallet(name=name, beekeeper=self.__beekeeper, session_token=self.token, guard=self.__guard)
        self.register_invalidable(wallet)
        return wallet

    def __list_wallets(self) -> list[WalletInterface]:
        return [
            self.__construct_wallet(name=wallet.name)
            for wallet in self.__beekeeper.api.list_wallets(token=self.token).wallets
        ]

    def __list_unlocked_wallets(self) -> list[UnlockedWalletInterface]:
        return [
            self.__construct_unlocked_wallet(name=wallet.name)
            for wallet in self.__beekeeper.api.list_wallets(token=self.token).wallets
            if wallet.unlocked
        ]

    def _enter(self) -> SessionInterface:
        return self

    def _finally(self) -> None:
        self.close_session()
