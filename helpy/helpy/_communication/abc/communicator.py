from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.settings_holder import SharedSettingsHolder
from helpy.exceptions import CommunicationError

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl


class AbstractCommunicator(SharedSettingsHolder[CommunicationSettings], ABC):
    """Provides basic interface for communicators, which can implement communications using different way."""

    @abstractmethod
    def _send(self, url: HttpUrl, data: bytes) -> str:
        """Sends to given url given data synchronously."""

    @abstractmethod
    async def _async_send(self, url: HttpUrl, data: bytes) -> str:
        """Sends to given url given data asynchronously."""

    async def _async_sleep_for_retry(self) -> None:
        """Sleeps using asyncio.sleep (for asynchronous implementations)."""
        await asyncio.sleep(self.settings.period_between_retries.total_seconds())

    def _sleep_for_retry(self) -> None:
        """Sleeps using time.sleep (for synchronous implementations)."""
        time.sleep(self.settings.period_between_retries.total_seconds())

    def _is_amount_of_retries_exceeded(self, amount: int) -> bool:
        """Returns is given amount of retries exceeds max_retries."""
        return amount > self.settings.max_retries

    @classmethod
    def _encode_data(cls, data: str) -> bytes:
        return data.encode("utf-8")

    @classmethod
    def _json_headers(cls) -> dict[str, str]:
        """Returns headers for json communication."""
        return {"Content-Type": "application/json"}

    @classmethod
    def _assert_status_code(cls, *, status_code: int, sent: str | bytes, received: str) -> None:
        """Checks is received status code is 2xx."""
        ok_status_code_lower_bound = 200
        ok_status_code_upper_bound = 299

        if not (ok_status_code_lower_bound <= status_code <= ok_status_code_upper_bound):
            raise CommunicationError(f"{status_code=}", f"{sent=}", f"{received=}")

    def send(self, url: HttpUrl, data: str) -> str:
        return self._send(url, self._encode_data(data))

    async def async_send(self, url: HttpUrl, data: str) -> str:
        return await self._async_send(url, self._encode_data(data))
