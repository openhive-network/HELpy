from __future__ import annotations

import schemas.beekeeper_api.response_schemas as beekeeper_api  # noqa: TCH001
from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from schemas.transaction_model.transaction import Hf26Transaction  # noqa: TCH001


class BeekeeperApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def create(self, *, wallet_name: str, password: str | None = None) -> beekeeper_api.Create:
        raise NotImplementedError

    @api
    def open(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:  # noqa: A003
        raise NotImplementedError

    @api
    def set_timeout(self, *, seconds: int) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock_all(self) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def unlock(self, *, wallet_name: str, password: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def import_key(self, *, wallet_name: str, wif_key: str) -> beekeeper_api.ImportKey:
        raise NotImplementedError

    @api
    def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def list_wallets(self) -> beekeeper_api.ListWallets:
        raise NotImplementedError

    @api
    def get_public_keys(self) -> beekeeper_api.GetPublicKeys:
        raise NotImplementedError

    @api
    def sign_digest(self, *, sig_digest: str, public_key: str) -> beekeeper_api.SignDigest:
        raise NotImplementedError

    @api
    def sign_transaction(
        self, *, transaction: Hf26Transaction, chain_id: str, public_key: str, sig_digest: str
    ) -> beekeeper_api.SignTransaction:
        raise NotImplementedError

    @api
    def get_info(self) -> beekeeper_api.GetInfo:
        raise NotImplementedError

    @api
    def create_session(self, *, notifications_endpoint: str, salt: str) -> beekeeper_api.CreateSession:
        raise NotImplementedError

    @api
    def close_session(self) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError
