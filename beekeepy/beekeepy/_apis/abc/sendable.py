from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.jsonrpc import ExpectResultT, JSONRPCResult


class SyncSendable(ABC):
    @abstractmethod
    def _send(
        self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]: ...


class AsyncSendable(ABC):
    @abstractmethod
    async def _async_send(
        self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]: ...
