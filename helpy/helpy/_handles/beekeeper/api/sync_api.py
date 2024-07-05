from __future__ import annotations

from typing import TYPE_CHECKING, cast

from helpy._handles.abc.api import AbstractSyncApi, ApiArgumentsToSerialize, SyncHandleT
from helpy._handles.beekeeper.api.apply_session_token import sync_apply_session_token
from helpy._handles.beekeeper.api.beekeeper_api_commons import BeekeeperApiCommons
from helpy._handles.beekeeper.api.session_holder import SyncSessionHolder
from schemas.apis import beekeeper_api  # noqa: TCH001

if TYPE_CHECKING:
    from helpy._handles.beekeeper.handle import Beekeeper, _SyncSessionBatchHandle


class BeekeeperApi(AbstractSyncApi, BeekeeperApiCommons[SyncHandleT]):
    api = AbstractSyncApi._endpoint

    _owner: Beekeeper | _SyncSessionBatchHandle

    def __init__(self, owner: Beekeeper | _SyncSessionBatchHandle) -> None:
        self._verify_is_owner_can_hold_session_token(owner=owner)
        super().__init__(owner=owner)

    def _additional_arguments_actions(
        self, endpoint_name: str, arguments: ApiArgumentsToSerialize
    ) -> ApiArgumentsToSerialize:
        if not self._token_required(endpoint_name):
            return super()._additional_arguments_actions(endpoint_name, arguments)
        return sync_apply_session_token(cast(SyncSessionHolder, self._owner), arguments)

    def _get_requires_session_holder_type(self) -> type[SyncSessionHolder]:
        return SyncSessionHolder

    @api
    def create(
        self, *, wallet_name: str, password: str | None = None, token: str | None = None
    ) -> beekeeper_api.Create:
        raise NotImplementedError

    @api
    def open(self, *, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def set_timeout(self, *, seconds: int, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock_all(self, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def lock(self, *, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def unlock(self, *, wallet_name: str, password: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def import_key(self, *, wallet_name: str, wif_key: str, token: str | None = None) -> beekeeper_api.ImportKey:
        raise NotImplementedError

    @api
    def import_keys(
        self, *, wallet_name: str, wif_keys: list[str], token: str | None = None
    ) -> beekeeper_api.ImportKeys:
        raise NotImplementedError

    @api
    def remove_key(self, *, wallet_name: str, public_key: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def list_wallets(self, token: str | None = None) -> beekeeper_api.ListWallets:
        raise NotImplementedError

    @api
    def list_created_wallets(self, token: str | None = None) -> beekeeper_api.ListWallets:
        raise NotImplementedError

    @api
    def get_public_keys(self, wallet_name: str | None = None, token: str | None = None) -> beekeeper_api.GetPublicKeys:
        raise NotImplementedError

    @api
    def sign_digest(
        self, *, sig_digest: str, public_key: str, wallet_name: str | None = None, token: str | None = None
    ) -> beekeeper_api.SignDigest:
        raise NotImplementedError

    @api
    def get_info(self, token: str | None = None) -> beekeeper_api.GetInfo:
        raise NotImplementedError

    @api
    def create_session(self, *, notifications_endpoint: str = "", salt: str = "") -> beekeeper_api.CreateSession:
        raise NotImplementedError

    @api
    def close_session(self, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def close(self, wallet_name: str, token: str | None = None) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def has_matching_private_key(
        self, wallet_name: str, public_key: str, token: str | None = None
    ) -> beekeeper_api.HasMatchingPrivateKey:
        raise NotImplementedError

    @api
    def encrypt_data(
        self,
        *,
        wallet_name: str,
        from_public_key: str,
        to_public_key: str,
        content: str,
        nonce: int | None = None,
        token: str | None = None,
    ) -> beekeeper_api.EncryptData:
        raise NotImplementedError

    @api
    def decrypt_data(
        self,
        *,
        wallet_name: str,
        from_public_key: str,
        to_public_key: str,
        encrypted_content: str,
        token: str | None = None,
    ) -> beekeeper_api.DecryptData:
        raise NotImplementedError
