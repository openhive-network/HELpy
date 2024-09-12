from __future__ import annotations

from helpy._handles.abc.api import AbstractSyncApi
from schemas.apis import network_broadcast_api  # noqa: TCH001
from schemas.transaction import Transaction  # noqa: TCH001


class NetworkBroadcastApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def broadcast_transaction(self, *, trx: Transaction) -> network_broadcast_api.BroadcastTransaction:
        raise NotImplementedError
