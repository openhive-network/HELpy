from __future__ import annotations

from typing import TYPE_CHECKING

from helpy._handles.abc.api import AbstractAsyncApi, ApiArgumentsToSerialize, AsyncHandleT
from helpy._handles.beekeeper.api.apply_session_token import async_apply_session_token
from helpy._handles.beekeeper.api.beekeeper_api_commons import BeekeeperApiCommons
from helpy._handles.beekeeper.api.session_holder import AsyncSessionHolder
from schemas.apis import beekeeper_api  # noqa: TCH001

if TYPE_CHECKING:
    from helpy._handles.beekeeper.handle import AsyncBeekeeper, _AsyncSessionBatchHandle


class BeekeeperApi(AbstractAsyncApi, BeekeeperApiCommons[AsyncHandleT]):
    """Set of endpoints, that allows asynchronous communication with beekeeper service."""

    api = AbstractAsyncApi._endpoint
    _owner: AsyncBeekeeper | _AsyncSessionBatchHandle

    def __init__(self, owner: AsyncBeekeeper | _AsyncSessionBatchHandle) -> None:
        self._verify_is_owner_can_hold_session_token(owner=owner)
        super().__init__(owner=owner)

    async def _additional_arguments_actions(
        self, endpoint_name: str, arguments: ApiArgumentsToSerialize
    ) -> ApiArgumentsToSerialize:
        if not self._token_required(endpoint_name):
            return await super()._additional_arguments_actions(endpoint_name, arguments)
        return await async_apply_session_token(self._owner, arguments)

    def _get_requires_session_holder_type(self) -> type[AsyncSessionHolder]:
        return AsyncSessionHolder

    @api
    async def create(
        self, *, wallet_name: str, password: str | None = None, token: str | None = None
    ) -> beekeeper_api.Create:
        """
        Creates wallet with given name.

        Args:
            wallet_name: name of wallet to create
            password: password for new wallet, if not given generates one. Defaults to None.

        Returns
            beekeeper_api.Create: Returns password that was used for wallet creation.
        """
        raise NotImplementedError

    @api
    async def open(self, *, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:  # noqa: A003
        """Opens wallet, which makes it unaccessible for other sessions.

        Args:
            wallet_name: wallet to open

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def set_timeout(self, *, seconds: int, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Sets timeout after all wallets opened in current session will be closed.

        Args:
            seconds: amount of seconds from last interaction (on any wallet) to wait before lock all wallets.

        Returns
            noting.
        """
        raise NotImplementedError

    @api
    async def lock_all(self, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Locks all wallet in current session.

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def lock(self, *, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Locks specific wallet.

        Args:
            wallet_name: wallet to lock.

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def unlock(self, *, wallet_name: str, password: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Unlocks specific wallet (and opens it implicitly).

        Args:
            wallet_name: wallet to unlock (and open)
            password: password to unlock wallet

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def import_key(self, *, wallet_name: str, wif_key: str, token: str | None = None) -> beekeeper_api.ImportKey:
        """Imports key to given wallet.

        Warning:
            After importing this key to beekeeper, it's impossible to access it via api; Access to private keys is only possible with binary.

        Args:
            wallet_name: wallet to import given key
            wif_key: private key to import

        Returns:
            Public key calculated from imported private key.
        """
        raise NotImplementedError

    @api
    async def remove_key(
        self, *, wallet_name: str, public_key: str, token: str | None = None
    ) -> beekeeper_api.EmptyResponse:
        """Removes imported key from given wallet.

        Args:
            wallet_name: wallet from key will be removed.
            public_key: public key, which is paired with private key to remove.

        Returns:
            beekeeper_api.EmptyResponse: Nothing.
        """
        raise NotImplementedError

    @api
    async def list_wallets(self, token: str | None = None) -> beekeeper_api.ListWallets:
        """Lists all opened wallets in current session.

        Note:
            Use `list_created_wallets` to get all (even not opened) wallets

        Returns:
            List of wallets
        """
        raise NotImplementedError

    @api
    async def list_created_wallets(self, token: str | None = None) -> beekeeper_api.ListWallets:
        """Lists all wallets existing in beekeeper.

        Returns:
            List of wallets
        """
        raise NotImplementedError

    @api
    async def get_public_keys(
        self, wallet_name: str | None = None, token: str | None = None
    ) -> beekeeper_api.GetPublicKeys:
        """Lists all public keys from all unlocked wallets.

        Args:
            wallet_name: if not None, beekeeper will list public keys only from given wallet

        Returns:
            List of public keys
        """
        raise NotImplementedError

    @api
    async def sign_digest(
        self, *, sig_digest: str, public_key: str, wallet_name: str | None = None, token: str | None = None
    ) -> beekeeper_api.SignDigest:
        """Signs given digest with private key paired with given public key.

        Args:
            sig_digest: digest to sign
            public_key: public key paired with private key to sign with
            wallet_name: if not set to None, beekeeper will use keys only from given wallet

        Returns:
            Signature
        """
        raise NotImplementedError

    @api
    async def get_info(self, token: str | None = None) -> beekeeper_api.GetInfo:
        """Gets status of current session.

        Returns:
            Information about current session.
        """
        raise NotImplementedError

    @api
    async def create_session(self, *, notifications_endpoint: str = "", salt: str = "") -> beekeeper_api.CreateSession:
        """Creates session.

        Note:
            This is called automatically when connection with beekeeper is establish, no need to call it explicitly.

        Args:
            notifications_endpoint: endpoint on which notifications of status will be broadcasted. (defaults: "")
            salt: used for generation of session token

        Returns:
            Session token.
        """
        raise NotImplementedError

    @api
    async def close_session(self, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Closes session.

        Returns:
            Noting.
        """
        raise NotImplementedError

    @api
    async def close(self, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        """Closes opened wallet, which implies locking.

        Args:
            wallet_name: wallet name to close

        Returns:
            Nothing
        """
        raise NotImplementedError

    @api
    async def has_matching_private_key(
        self, wallet_name: str, public_key: str, token: str | None = None
    ) -> beekeeper_api.HasMatchingPrivateKey:
        """Checks is beekeeper contain private key associated with given public key.

        Args:
            wallet_name: wallet to check for corresponding private key
            public_key: public key to check

        Returns:
            True if found, False otherwise
        """
        raise NotImplementedError
