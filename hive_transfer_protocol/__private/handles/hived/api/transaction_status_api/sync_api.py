from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from schemas.transaction_status_api.response_schemas import FindTransaction  # noqa: TCH001


class TransactionStatusApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def find_transaction(self, *, transaction_id: str, expiration: datetime | None = None) -> FindTransaction:
        raise NotImplementedError
