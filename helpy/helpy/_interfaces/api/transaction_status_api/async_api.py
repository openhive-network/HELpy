from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import transaction_status_api  # noqa: TCH001


class TransactionStatusApi(AbstractAsyncApi):
    @AbstractAsyncApi._endpoint
    async def find_transaction(
        self, *, transaction_id: str, expiration: datetime | None = None
    ) -> transaction_status_api.FindTransaction:
        raise NotImplementedError
