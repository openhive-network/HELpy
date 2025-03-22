from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import TYPE_CHECKING, Any, Awaitable

from beekeepy._communication.settings import CommunicationSettings
from beekeepy._utilities.settings_holder import SharedSettingsHolder
from beekeepy._utilities.stopwatch import Stopwatch
from beekeepy.exceptions import CommunicationError, TimeoutExceededError, UnknownDecisionPathError

if TYPE_CHECKING:
    from beekeepy._communication.url import HttpUrl
    from beekeepy._utilities.stopwatch import StopwatchResult


class AbstractCommunicator(SharedSettingsHolder[CommunicationSettings], ABC):
    """Provides basic interface for communicators, which can implement communications using different way."""

    @abstractmethod
    def _send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        """Sends to given url given data synchronously."""

    @abstractmethod
    async def _async_send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        """Sends to given url given data asynchronously."""

    @abstractmethod
    def teardown(self) -> None:
        """Called when work with communicator is over."""

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
        with Stopwatch() as sp:
            return self._send(url, self._encode_data(data), sp)
        raise UnknownDecisionPathError

    async def async_send(self, url: HttpUrl, data: str) -> str:
        with Stopwatch() as sp:
            return await self._async_send(url, self._encode_data(data), sp)
        raise UnknownDecisionPathError

    def _construct_timeout_exception(self, url: HttpUrl, data: bytes, total_time_secs: float) -> TimeoutExceededError:
        return TimeoutExceededError(
            url=url, request=data, timeout_secs=self.settings.timeout.total_seconds(), total_wait_time=total_time_secs
        )

    def _asyncio_run(self, coro: Awaitable[Any]) -> None:
        thread = Thread(target=asyncio.run, args=(coro,))
        thread.start()
        thread.join()
