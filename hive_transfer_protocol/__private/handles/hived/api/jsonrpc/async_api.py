from __future__ import annotations

from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi
from schemas.jsonrpc import response_schemas as jsonrpc  # noqa: TCH001


class Jsonrpc(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_methods(self) -> jsonrpc.GetMethods:
        raise NotImplementedError

    @api
    async def get_signature(self, *, method: str = "") -> jsonrpc.GetSignature:
        raise NotImplementedError
