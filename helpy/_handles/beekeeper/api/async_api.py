from __future__ import annotations

from typing import Any

from helpy._handles.abc.api import AbstractAsyncApi
from helpy._handles.beekeeper.api.apply_session_token import apply_session_token
from helpy._handles.beekeeper.api.session_holder import SessionHolder
from schemas.apis import beekeeper_api  # noqa: TCH001


class BeekeeperApi(AbstractAsyncApi):
    """Set of endpoints, that allows asynchronous communication with beekeeper service."""

    api = AbstractAsyncApi._endpoint

    def _additional_arguments_actions(
        self, endpoint_name: str, *args: Any, **kwargs: Any
    ) -> tuple[list[Any], dict[str, Any]]:
        if "create_session" in endpoint_name:
            return super()._additional_arguments_actions(endpoint_name, *args, **kwargs)
        assert isinstance(self._owner, SessionHolder), f"owner `{self._owner}` is not able to handle this request"
        return apply_session_token(self._owner, list(args), kwargs)

    @api
    async def create(self, *, wallet_name: str, password: str | None = None) -> beekeeper_api.Create:
        """
        Creates wallet with given name.

        Arguments:
        ----
            wallet_name (str) -- name of wallet to create
            password (str | None, optional) -- password for new wallet, if not given generates one. Defaults to None.

        Returns
        -------
            beekeeper_api.Create: Returns password that was used for wallet creation.
        """
        raise NotImplementedError

    @api
    async def open(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:  # noqa: A003
        """Opens wallet, which makes it unaccessible for other sessions.

        Arguments:
            wallet_name (str) -- wallet to open

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def set_timeout(self, *, seconds: int) -> beekeeper_api.EmptyResponse:
        """Sets timeout after all wallets opened in current session will be closed.

        Arguments:
            seconds -- amount of seconds from last interaction (on any wallet) to wait before lock all wallets.

        Returns
        -------
            noting.
        """
        raise NotImplementedError

    @api
    async def lock_all(self) -> beekeeper_api.EmptyResponse:
        """Locks all wallet in current session.

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def lock(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:
        """Locks specific wallet.

        Arguments:
            wallet_name -- wallet to lock.

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def unlock(self, *, wallet_name: str, password: str) -> beekeeper_api.EmptyResponse:
        """Unlocks specific wallet (and opens it implicitly).

        Arguments:
            wallet_name -- wallet to unlock (and open)
            password -- password to unlock wallet

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def import_key(self, *, wallet_name: str, wif_key: str) -> beekeeper_api.ImportKey:
        """Imports key to given wallet.

        Warning:
            After importing this key to beekeeper, it's impossible to access it via api; Access to private keys is only possible with binary.

        Arguments:
            wallet_name -- wallet to import given key
            wif_key -- private key to import

        Returns:
            Public key calculated from imported private key.
        """
        raise NotImplementedError

    @api
    async def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> beekeeper_api.EmptyResponse:
        """Removes imported key from given wallet.

        Arguments:
            wallet_name -- wallet from key will be removed
            password -- to confirm action
            public_key -- public key, which is paired with private key to remove

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def list_wallets(self) -> beekeeper_api.ListWallets:
        """Lists all opened wallets in current session.

        Note:
            There is no way to list all not opened wallets.

        Returns:
            List of wallets
        """
        raise NotImplementedError

    @api
    async def get_public_keys(self, wallet_name: str | None = None) -> beekeeper_api.GetPublicKeys:
        """Lists all public keys from all unlocked wallets.

        Arguments:
            wallet_name -- if not None, beekeeper will list public keys only from given wallet

        Returns:
            List of public keys
        """
        raise NotImplementedError

    @api
    async def sign_digest(
        self, *, sig_digest: str, public_key: str, wallet_name: str | None = None
    ) -> beekeeper_api.SignDigest:
        """Signs given digest with private key paired with given public key.

        Arguments:
            sig_digest -- digest to sign
            public_key -- public key paired with private key to sign with
            wallet_name -- if not set to None, beekeeper will use keys only from given wallet

        Returns:
            Signature
        """
        raise NotImplementedError

    @api
    async def get_info(self) -> beekeeper_api.GetInfo:
        """Gets status of current session.

        Returns:
            Information about current session.
        """
        raise NotImplementedError

    @api
    async def create_session(self, *, notifications_endpoint: str, salt: str) -> beekeeper_api.CreateSession:
        """Creates session.

        Note:
            This is called automatically when connection with beekeeper is establish, no need to call it explicitly.

        Arguments:
            notifications_endpoint -- endpoint on which notifications of status will be broadcasted.
            salt -- used for generation of session token

        Returns:
            Session token
        """
        raise NotImplementedError

    @api
    async def close_session(self) -> beekeeper_api.EmptyResponse:
        """Closes session.

        Returns:
            Noting.
        """
        raise NotImplementedError

    @api
    async def close(self, wallet_name: str) -> beekeeper_api.EmptyResponse:
        """Closes opened wallet, which implies locking.

        Arguments:
            wallet_name -- wallet name to close

        Returns:
            Nothing
        """
        raise NotImplementedError

    @api
    async def has_matching_private_key(self, wallet_name: str, public_key: str) -> beekeeper_api.HasMatchingPrivateKey:
        """Checks is beekeeper contain private key associated with given public key.

        Arguments:
            wallet_name -- wallet to check for corresponding private key
            public_key -- public key to check

        Returns:
            True if found, False otherwise
        """
        raise NotImplementedError
