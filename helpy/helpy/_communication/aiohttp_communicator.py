from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

from helpy._communication.abc.communicator import (
    AbstractCommunicator,
)
from helpy.exceptions import CommunicationError

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl


class AioHttpCommunicator(AbstractCommunicator):
    """Provides support for aiohttp library."""

    async def _async_send(self, url: HttpUrl, data: bytes) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.settings.timeout.total_seconds())
            ) as session:
                try:
                    response = await session.post(
                        url.as_string(),
                        data=data,
                        headers=self._json_headers(),
                    )
                    return await response.text()
                except aiohttp.ClientConnectorError as error:
                    raise CommunicationError(url=url.as_string(), request=data) from error
                except aiohttp.ClientError as error:
                    last_exception = error
                await self._async_sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception

    def _send(self, url: HttpUrl, data: bytes) -> str:
        raise NotImplementedError
