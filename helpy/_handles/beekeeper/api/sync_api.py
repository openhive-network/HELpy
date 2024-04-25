from __future__ import annotations

from typing import Any

from helpy._handles.abc.api import AbstractSyncApi
from helpy._handles.beekeeper.api.apply_session_token import apply_session_token
from helpy._handles.beekeeper.api.session_holder import SessionHolder
from schemas.apis import beekeeper_api  # noqa: TCH001


class BeekeeperApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    def _additional_arguments_actions(
        self, endpoint_name: str, *args: Any, **kwargs: Any
    ) -> tuple[list[Any], dict[str, Any]]:
        if "create_session" in endpoint_name:
            return (list(args), kwargs)
        assert isinstance(self._owner, SessionHolder), f"owner `{self._owner}` is not able to handle this request"
        return apply_session_token(self._owner, list(args), kwargs)

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
    def get_public_keys(self, wallet_name: str | None = None) -> beekeeper_api.GetPublicKeys:
        raise NotImplementedError

    @api
    def sign_digest(
        self, *, sig_digest: str, public_key: str, wallet_name: str | None = None
    ) -> beekeeper_api.SignDigest:
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

    @api
    def close(self, wallet_name: str) -> beekeeper_api.EmptyResponse:
        raise NotImplementedError

    @api
    def has_matching_private_key(self, wallet_name: str, public_key: str) -> beekeeper_api.HasMatchingPrivateKey:
        raise NotImplementedError
