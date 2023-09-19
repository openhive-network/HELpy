from __future__ import annotations

from helpy.__private.handles.abc.api import AbstractSyncApi
from schemas.account_by_key_api.response_schemas import GetKeyReferences  # noqa: TCH001


class AccountByKeyApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def get_key_references(self, *, accounts: list[str]) -> GetKeyReferences:
        raise NotImplementedError
