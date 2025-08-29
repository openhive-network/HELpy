from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from functools import wraps
from typing import TYPE_CHECKING, Any, Generic, NoReturn, ParamSpec, TypeVar, overload

from beekeepy._interface.settings import InterfaceSettings
from beekeepy._remote_handle import AsyncBeekeeperTemplate as AsyncRemoteBeekeeper
from beekeepy._remote_handle import BeekeeperTemplate as SyncRemoteBeekeeper
from beekeepy._runnable_handle import AsyncWalletLocked, SyncWalletLocked
from beekeepy._utilities.delay_guard import AsyncDelayGuard, SyncDelayGuard
from beekeepy._utilities.state_invalidator import StateInvalidator
from beekeepy.exceptions import WalletIsLockedError
from beekeepy.exceptions.overseer import UnlockIsNotAccessibleError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from schemas.apis.beekeeper_api.fundaments_of_responses import WalletDetails

P = ParamSpec("P")
ResultT = TypeVar("ResultT")
BeekeeperT = TypeVar(
    "BeekeeperT", bound=SyncRemoteBeekeeper[InterfaceSettings] | AsyncRemoteBeekeeper[InterfaceSettings]
)
CallbackT = TypeVar("CallbackT", bound=AsyncWalletLocked | SyncWalletLocked)
GuardT = TypeVar("GuardT", bound=SyncDelayGuard | AsyncDelayGuard)


class ContainsWalletName(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...


class WalletCommons(ContainsWalletName, StateInvalidator, Generic[BeekeeperT, CallbackT, GuardT]):
    def __init__(
        self, *args: Any, name: str, beekeeper: BeekeeperT, session_token: str, guard: GuardT, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__name = name
        self.__beekeeper = beekeeper
        self.__last_check_is_locked = True
        self.__wallet_close_callbacks: list[CallbackT] = []
        self.session_token = session_token
        self._guard = guard

    def register_wallet_close_callback(self, callback: CallbackT) -> None:
        self._wallet_close_callbacks.append(callback)

    @property
    def _wallet_close_callbacks(self) -> list[CallbackT]:
        return self.__wallet_close_callbacks

    @property
    def name(self) -> str:
        return self.__name

    @property
    def _beekeeper(self) -> BeekeeperT:
        return self.__beekeeper

    @property
    def _last_lock_state(self) -> bool:
        """Returns last save lock state.

        True: last state of wallet was locked
        False: last state of wallet was unlocked
        """
        return self.__last_check_is_locked

    @_last_lock_state.setter
    def _last_lock_state(self, value: bool) -> None:
        self.__last_check_is_locked = value

    def _is_wallet_unlocked(self, *, wallet_name: str, wallets: list[WalletDetails]) -> bool:
        """Checks is wallet locked.

        Args:
            wallet_name: wallet to check is locked
            wallets: collection of wallets from api

        Returns:
            True if given wallet is locked (or not found), False if wallet is unlocked.
        """
        for wallet in wallets:
            if wallet.name == wallet_name:
                self._last_lock_state = wallet.unlocked
                return wallet.unlocked
        self._last_lock_state = False
        return False

    def _raise_wallet_is_locked_error(self, exception: Exception) -> NoReturn:
        raise WalletIsLockedError(wallet_name=self.name) from exception

    def __get_all_locked_wallets(self, api_result: list[WalletDetails]) -> list[str]:
        """Returns a list of all locked wallet names."""
        return [wallet.name for wallet in api_result if not wallet.unlocked]

    async def _async_call_callback(self) -> None:
        assert isinstance(self._beekeeper, AsyncRemoteBeekeeper), "invalid beekeeper type, require synchronous"

        locked_wallets = self.__get_all_locked_wallets(
            (await self._beekeeper.api.list_wallets(token=self.session_token)).wallets
        )
        if not locked_wallets:
            return
        await asyncio.gather(
            *[
                callback(locked_wallets)
                for callback in self._wallet_close_callbacks
                if asyncio.iscoroutinefunction(callback)
            ]
        )

    def _sync_call_callback(self) -> None:
        assert isinstance(self._beekeeper, SyncRemoteBeekeeper), "invalid beekeeper type, require synchronous"

        locked_wallets = self.__get_all_locked_wallets(
            self._beekeeper.api.list_wallets(token=self.session_token).wallets
        )
        if not locked_wallets:
            return

        for callback in self.__wallet_close_callbacks:
            callback(locked_wallets)

    @overload
    @classmethod
    def check_wallet(cls, wrapped_function: Callable[P, ResultT]) -> Callable[P, ResultT]: ...

    @overload
    @classmethod
    def check_wallet(cls, wrapped_function: Callable[P, Awaitable[ResultT]]) -> Callable[P, Awaitable[ResultT]]: ...

    @classmethod  # type: ignore[misc]
    def check_wallet(
        cls, wrapped_function: Callable[P, Awaitable[ResultT]] | Callable[P, ResultT]
    ) -> Callable[P, Awaitable[ResultT]] | Callable[P, ResultT]:
        if iscoroutinefunction(wrapped_function):

            @wraps(wrapped_function)
            async def async_impl(*args: P.args, **kwrags: P.kwargs) -> ResultT:
                this: WalletCommons[AsyncRemoteBeekeeper[InterfaceSettings], AsyncWalletLocked, AsyncDelayGuard] = args[
                    0
                ]  # type: ignore[assignment]
                try:
                    return await wrapped_function(*args, **kwrags)  # type: ignore[no-any-return]
                except UnlockIsNotAccessibleError as ex:
                    await this._async_call_callback()
                    this._raise_wallet_is_locked_error(ex)

            return async_impl

        @wraps(wrapped_function)
        def sync_impl(*args: P.args, **kwrags: P.kwargs) -> ResultT:
            this: WalletCommons[SyncRemoteBeekeeper[InterfaceSettings], SyncWalletLocked, SyncDelayGuard] = args[0]  # type: ignore[assignment]
            try:
                return wrapped_function(*args, **kwrags)  # type: ignore[return-value]
            except UnlockIsNotAccessibleError as ex:
                this._sync_call_callback()
                this._raise_wallet_is_locked_error(ex)

        return sync_impl
