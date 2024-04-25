from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from helpy._communication.abc.communicator import (
    AbstractCommunicator,
)
from helpy.exceptions import CommunicationError

if TYPE_CHECKING:
    from helpy._communication.settings import CommunicationSettings
    from helpy._interfaces.url import HttpUrl


class HttpxCommunicator(AbstractCommunicator):
    """Provides support for httpx library."""

    def __init__(self, settings: CommunicationSettings) -> None:
        super().__init__(settings=settings)
        self.__async_client: httpx.AsyncClient | None = httpx.AsyncClient(
            timeout=self.settings.timeout.total_seconds(), http2=True
        )

    async def close(self) -> None:
        if self.__async_client is not None:
            await self.__async_client.aclose()
            self.__async_client = None

    def get_async_client(self) -> httpx.AsyncClient:
        assert self.__async_client is not None, "Session is closed."
        return self.__async_client

    async def async_send(self, url: HttpUrl, data: str) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = await self.get_async_client().post(
                    url.as_string(), content=data, headers=self._json_headers()
                )
                data_received = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.ConnectError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except httpx.HTTPError as error:
                last_exception = error
            await self._async_sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception

    def send(self, url: HttpUrl, data: str) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = httpx.post(url.as_string(), content=data, headers=self._json_headers())
                data_received = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.ConnectError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except httpx.HTTPError as error:
                last_exception = error
            self._sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception
