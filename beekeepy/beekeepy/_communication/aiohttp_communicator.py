from __future__ import annotations

import asyncio
import asyncio.exceptions
from typing import TYPE_CHECKING, Any

import aiohttp

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError, UnknownDecisionPathError

if TYPE_CHECKING:
    from beekeepy._communication.settings import CommunicationSettings
    from beekeepy._interface.stopwatch import StopwatchResult
    from beekeepy._interface.url import HttpUrl


class AioHttpCommunicator(AbstractCommunicator):
    """Provides support for aiohttp library."""

    def __init__(self, *args: Any, settings: CommunicationSettings, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, **kwargs)
        self.__session: aiohttp.ClientSession | None = None

    @property
    async def session(self) -> aiohttp.ClientSession:
        if self.__session is None:
            self.__session = aiohttp.ClientSession(
                headers=self._json_headers(), timeout=aiohttp.ClientTimeout(total=self.settings.timeout.total_seconds())
            )
        return self.__session

    async def _async_send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                async with (await self.session).post(url.as_string(), data=data) as response:
                    return await response.text()
            except (aiohttp.ServerTimeoutError, asyncio.TimeoutError):
                last_exception = self._construct_timeout_exception(url, data, stopwatch.lap)
            except aiohttp.ClientConnectorError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except aiohttp.ClientError as error:
                last_exception = error
            await self._async_sleep_for_retry()

        if last_exception is None:
            raise UnknownDecisionPathError("Retry loop finished, but last_exception was not set")
        raise last_exception

    def _send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        raise NotImplementedError

    def teardown(self) -> None:
        if self.__session is not None:
            self._asyncio_run(self.__session.close())
