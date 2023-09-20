from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar

from helpy.exceptions import HelpyError

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl


class CommunicationError(HelpyError):
    """Base class for all communication related errors."""


class ExceededAmountOfRetriesError(CommunicationError):
    """Raised if exceeded amount of retries."""


class AbstractCommunicator(ABC):
    """Provides basic interface for communicators, which can implement communications using different way."""

    max_retries: ClassVar[int] = 5
    period_between_retries: ClassVar[timedelta] = timedelta(seconds=1)
    timeout: ClassVar[timedelta] = timedelta(seconds=2)

    @abstractmethod
    def send(self, url: HttpUrl, data: str) -> str:
        """Sends to given url given data synchronously."""

    @abstractmethod
    async def async_send(self, url: HttpUrl, data: str) -> str:
        """Sends to given url given data asynchronously."""

    @classmethod
    async def _async_sleep_for_retry(cls) -> None:
        """Sleeps using asyncio.sleep (for asynchronous implementations)."""
        await asyncio.sleep(cls.period_between_retries.total_seconds())

    @classmethod
    def _sleep_for_retry(cls) -> None:
        """Sleeps using time.sleep (for synchronous implementations)."""
        time.sleep(cls.period_between_retries.total_seconds())

    @classmethod
    def _is_amount_of_retries_exceeded(cls, amount: int) -> bool:
        """Returns is given amount of retries exceeds max_retries."""
        return amount > cls.max_retries

    @classmethod
    def _assert_is_amount_of_retries_exceeded(cls, amount: int) -> None:
        """Checks is given amount of retries exceeds max_retries and if so raises ExceededAmountOfRetriesError."""
        if cls._is_amount_of_retries_exceeded(amount=amount):
            raise ExceededAmountOfRetriesError

    @classmethod
    def _json_headers(cls) -> dict[str, str]:
        """Returns headers for json communication."""
        return {"Content-Type": "application/json"}

    @classmethod
    def _assert_status_code(cls, *, status_code: int, sent: str, received: str) -> None:
        """Checks is received status code is 2xx."""
        ok_status_code_lower_bound = 200
        ok_status_code_upper_bound = 299

        if not (ok_status_code_lower_bound <= status_code <= ok_status_code_upper_bound):
            raise CommunicationError(f"{status_code=}", f"{sent=}", f"{received=}")
