from __future__ import annotations

from helpy._handles.abc.api import AbstractAsyncApi
from schemas.apis import account_by_key_api  # noqa: TCH001


class AccountByKeyApi(AbstractAsyncApi):
    @AbstractAsyncApi._endpoint
    async def get_key_references(self, *, keys: list[str]) -> account_by_key_api.GetKeyReferences:
        raise NotImplementedError
