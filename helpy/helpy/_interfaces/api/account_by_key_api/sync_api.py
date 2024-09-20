from __future__ import annotations

from helpy._interfaces.api.abc import AbstractSyncApi
from schemas.apis import account_by_key_api  # noqa: TCH001


class AccountByKeyApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def get_key_references(self, *, keys: list[str]) -> account_by_key_api.GetKeyReferences:
        raise NotImplementedError
