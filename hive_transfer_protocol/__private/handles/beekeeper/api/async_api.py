from __future__ import annotations

import schemas.beekeeper_api.response_schemas as beekeeper_api  # noqa: TCH001
from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi
from schemas.transaction_model.transaction import Hf26Transaction  # noqa: TCH001


class BeekeeperApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def create(self, *, wallet_name: str, password: str | None = None) -> beekeeper_api.Create:
        raise NotImplementedError

    @api
    async def open(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:  # noqa: A003
        raise NotImplementedError

    @api
    async def set_timeout(self, *, seconds: int) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    async def lock_all(self) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    async def lock(self, *, wallet_name: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    async def unlock(self, *, wallet_name: str, password: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    async def import_key(self, *, wallet_name: str, wif_key: str) -> beekeeper_api.ImportKey:
        raise NotImplementedError

    @api
    async def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    async def list_wallets(self) -> beekeeper_api.ListWallets:
        raise NotImplementedError

    @api
    async def list_keys(self, *, wallet_name: str, password: str) -> beekeeper_api.ListKeys:
        raise NotImplementedError

    @api
    async def get_public_keys(self) -> beekeeper_api.GetPublicKeys:
        raise NotImplementedError

    @api
    async def sign_digest(self, *, sig_digest: str, public_key: str) -> beekeeper_api.SignDigest:
        raise NotImplementedError

    @api
    async def sign_transaction(
        self, *, transaction: Hf26Transaction, chain_id: str, public_key: str, sig_digest: str
    ) -> beekeeper_api.SignTransaction:
        raise NotImplementedError

    @api
    async def get_info(self) -> beekeeper_api.GetInfo:
        raise NotImplementedError

    @api
    async def create_session(self, *, notifications_endpoint: str, salt: str) -> beekeeper_api.CreateSession:
        raise NotImplementedError

    @api
    async def close_session(self) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError
