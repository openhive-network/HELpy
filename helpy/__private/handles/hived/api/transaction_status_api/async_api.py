from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from helpy.__private.handles.abc.api import AbstractAsyncApi
from schemas.transaction_status_api.response_schemas import FindTransaction  # noqa: TCH001


class TransactionStatusApi(AbstractAsyncApi):
    @AbstractAsyncApi._endpoint
    async def find_transaction(self, *, transaction_id: str, expiration: datetime | None = None) -> FindTransaction:
        raise NotImplementedError
