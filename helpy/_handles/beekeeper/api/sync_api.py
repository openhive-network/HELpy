from __future__ import annotations

from helpy._handles.abc.api import AbstractSyncApi
from schemas.apis import beekeeper_api  # noqa: TCH001
from schemas.transaction import Transaction  # noqa: TCH001


class BeekeeperApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def create(self, *, token: str, wallet_name: str, password: str | None = None) -> beekeeper_api.Create:
        raise NotImplementedError

    @api
    def open(self, *, token: str, wallet_name: str) -> beekeeper_api.EmptyResponse:  # noqa: A003
        raise NotImplementedError

    @api
    def set_timeout(self, *, token: str, seconds: int) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock_all(self, *, token: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock(self, *, token: str, wallet_name: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def unlock(self, *, token: str, wallet_name: str, password: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def import_key(self, *, token: str, wallet_name: str, wif_key: str) -> beekeeper_api.ImportKey:
        raise NotImplementedError

    @api
    def remove_key(
        self, *, token: str, wallet_name: str, password: str, public_key: str
    ) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def list_wallets(self, *, token: str) -> beekeeper_api.ListWallets:
        raise NotImplementedError

    @api
    def get_public_keys(self, *, token: str) -> beekeeper_api.GetPublicKeys:
        raise NotImplementedError

    @api
    def sign_digest(self, *, token: str, sig_digest: str, public_key: str) -> beekeeper_api.SignDigest:
        raise NotImplementedError

    @api
    def sign_transaction(
        self, *, token: str, transaction: Transaction, chain_id: str, public_key: str, sig_digest: str
    ) -> beekeeper_api.SignTransaction:
        raise NotImplementedError

    @api
    def get_info(self, *, token: str) -> beekeeper_api.GetInfo:
        raise NotImplementedError

    @api
    def create_session(self, *, notifications_endpoint: str, salt: str) -> beekeeper_api.CreateSession:
        raise NotImplementedError

    @api
    def close_session(self, *, token: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError
