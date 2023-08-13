from __future__ import annotations

from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi
from schemas.account_by_key_api.response_schemas import GetKeyReferences  # noqa: TCH001


class AccountByKeyApi(AbstractAsyncApi):
    @AbstractAsyncApi._endpoint
    async def get_key_references(self, *, accounts: list[str]) -> GetKeyReferences:
        raise NotImplementedError
