from __future__ import annotations

from helpy.__private.handles.abc.api import AbstractSyncApi
from schemas.jsonrpc import response_schemas as jsonrpc  # noqa: TCH001


class Jsonrpc(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def get_methods(self) -> jsonrpc.GetMethods:
        raise NotImplementedError

    @api
    def get_signature(self, *, method: str = "") -> jsonrpc.GetSignature:
        raise NotImplementedError
