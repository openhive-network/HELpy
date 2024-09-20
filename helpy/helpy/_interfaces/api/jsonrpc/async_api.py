from __future__ import annotations

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import jsonrpc  # noqa: TCH001


class Jsonrpc(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_methods(self) -> jsonrpc.GetMethods:
        raise NotImplementedError

    @api
    async def get_signature(self, *, method: str = "") -> jsonrpc.GetSignature:
        raise NotImplementedError
