from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from helpy.__private.handles.abc.api import AbstractSyncApi
from schemas.apis import transaction_status_api  # noqa: TCH001


class TransactionStatusApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def find_transaction(
        self, *, transaction_id: str, expiration: datetime | None = None
    ) -> transaction_status_api.FindTransaction:
        raise NotImplementedError
