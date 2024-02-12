from __future__ import annotations

from helpy._handles.abc.api import AbstractAsyncApi
from schemas.apis import beekeeper_api  # noqa: TCH001
from schemas.transaction import Transaction  # noqa: TCH001


class BeekeeperApi(AbstractAsyncApi):
    """Set of endpoints, that allows asynchronous communication with beekeeper service."""

    api = AbstractAsyncApi._endpoint

    @api
    async def create(self, *, token: str, wallet_name: str, password: str | None = None) -> beekeeper_api.Create:
        """
        Creates wallet with given name.

        Arguments:
            token (str) -- valid session token
            wallet_name (str) -- name of wallet to create
            password (str | None, optional) -- password for new wallet, if not given generates one. Defaults to None.

        Returns
            beekeeper_api.Create: Returns password that was used for wallet creation.
        """
        raise NotImplementedError

    @api
    async def open(self, *, token: str, wallet_name: str) -> beekeeper_api.EmptyResponse:  # noqa: A003
        """Opens wallet, which makes it unaccessible for other sessions.

        Arguments:
            token (str) -- valid session token
            wallet_name (str) -- wallet to open

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def set_timeout(self, *, token: str, seconds: int) -> beekeeper_api.EmptyResponse:
        """Sets timeout after all wallets opened in current session will be closed.

        Arguments:
            token (str) -- valid session token
            seconds -- amount of seconds from last interaction (on any wallet) to wait before lock all wallets.

        Returns
        -------
            noting.
        """
        raise NotImplementedError

    @api
    async def lock_all(self, *, token: str) -> beekeeper_api.EmptyResponse:
        """Locks all wallet in current session.

        Arguments:
            token (str) -- valid session token

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def lock(self, *, token: str, wallet_name: str) -> beekeeper_api.EmptyResponse:
        """Locks specific wallet.

        Arguments:
            token (str) -- valid session token
            wallet_name -- wallet to lock.

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def unlock(self, *, token: str, wallet_name: str, password: str) -> beekeeper_api.EmptyResponse:
        """Unlocks specific wallet (and opens it implicitly).

        Arguments:
            token (str) -- valid session token
            wallet_name -- wallet to unlock (and open)
            password -- password to unlock wallet

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def import_key(self, *, token: str, wallet_name: str, wif_key: str) -> beekeeper_api.ImportKey:
        """Imports key to given wallet.

        Warning:
            After importing this key to beekeeper, it's impossible to access it via api; Access to private keys is only possible with binary.

        Arguments:
            token (str) -- valid session token
            wallet_name -- wallet to import given key
            wif_key -- private key to import

        Returns:
            Public key calculated from imported private key.
        """
        raise NotImplementedError

    @api
    async def remove_key(
        self, *, token: str, wallet_name: str, password: str, public_key: str
    ) -> beekeeper_api.EmptyResponse:
        """Removes imported key from given wallet.

        Arguments:
            token (str) -- valid session token
            wallet_name -- wallet from key will be removed
            password -- to confirm action
            public_key -- public key, which is paired with private key to remove

        Returns:
            Nothing.
        """
        raise NotImplementedError

    @api
    async def list_wallets(self, *, token: str) -> beekeeper_api.ListWallets:
        """Lists all opened wallets in current session.

        Note:
            There is no way to list all not opened wallets.

        Arguments:
            token (str) -- valid session token

        Returns:
            List of wallets
        """
        raise NotImplementedError

    @api
    async def get_public_keys(self, *, token: str) -> beekeeper_api.GetPublicKeys:
        """Lists all public keys from all unlocked wallets.

        Arguments:
            token (str) -- valid session token

        Returns:
            List of public keys
        """
        raise NotImplementedError

    @api
    async def sign_digest(self, *, token: str, sig_digest: str, public_key: str) -> beekeeper_api.SignDigest:
        """Signs given digest with private key paired with given public key.

        Arguments:
            token (str) -- valid session token
            sig_digest -- digest to sign
            public_key -- public key paired with private key to sign with

        Returns:
            Signature
        """
        raise NotImplementedError

    @api
    async def sign_transaction(
        self, *, token: str, transaction: Transaction, chain_id: str, public_key: str, sig_digest: str
    ) -> beekeeper_api.SignTransaction:
        """Signs transaction with given key.

        Arguments:
            token (str) -- valid session token
            transaction -- transaction to sign
            chain_id -- chain id under which signature should be created (database_api.get_config -> HIVE_CHAIN_ID)
            public_key -- public key paired with private key to sign with
            sig_digest -- sig digest of given transaction to confirm proper transaction will be signed

        Returns:
            Signature
        """
        raise NotImplementedError

    @api
    async def get_info(self, *, token: str) -> beekeeper_api.GetInfo:
        """Gets status of current session.

        Arguments:
            token (str) -- valid session token

        Returns:
            Information about current session.
        """
        raise NotImplementedError

    @api
    async def create_session(
        self, *, token: str, notifications_endpoint: str, salt: str
    ) -> beekeeper_api.CreateSession:
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
    async def close_session(self, *, token: str) -> beekeeper_api.EmptyResponse:
        """Closes session.

        Arguments:
            token (str) -- valid session token

        Returns:
            Noting.
        """
        raise NotImplementedError
