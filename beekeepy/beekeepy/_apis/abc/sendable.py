from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from schemas.jsonrpc import ExpectResultT, JSONRPCResult


class SyncSendable(ABC):
    @abstractmethod
    def _send(
        self,
        *,
        endpoint: str,
        params: str,
        expected_type: type[ExpectResultT],
        serialization_type: Literal["hf26", "legacy"],
    ) -> JSONRPCResult[ExpectResultT]: ...

    @abstractmethod
    def is_testnet(self) -> bool:
        """Check if the current instance is connected to a testnet."""


class AsyncSendable(ABC):
    @abstractmethod
    async def _async_send(
        self,
        *,
        endpoint: str,
        params: str,
        expected_type: type[ExpectResultT],
        serialization_type: Literal["hf26", "legacy"],
    ) -> JSONRPCResult[ExpectResultT]: ...

    @abstractmethod
    def is_testnet(self) -> bool:
        """Check if the current instance is connected to a testnet."""
