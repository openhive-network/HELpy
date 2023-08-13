from __future__ import annotations

from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from schemas.network_broadcast_api.response_schemas import BroadcastTransaction  # noqa: TCH001
from schemas.transaction_model.transaction import Hf26Transaction  # noqa: TCH001


class NetworkBroadcastApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def broadcast_transaction(self, *, trx: Hf26Transaction) -> BroadcastTransaction:
        raise NotImplementedError
