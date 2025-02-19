from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from beekeepy._communication.settings import CommunicationSettings
    from beekeepy._interface.stopwatch import StopwatchResult
    from beekeepy._interface.url import HttpUrl

ClientTypes = httpx.AsyncClient | httpx.Client


class HttpxCommunicator(AbstractCommunicator):
    """Provides support for httpx library."""

    def __init__(self, *args: Any, settings: CommunicationSettings, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, **kwargs)
        self.__async_client: httpx.AsyncClient | None = None
        self.__sync_client: httpx.Client | None = None

    def teardown(self) -> None:
        if self.__async_client is not None:
            self._asyncio_run(self.__async_client.aclose())
            self.__async_client = None

        if self.__sync_client is not None:
            self.__sync_client.close()
            self.__sync_client = None

    def __create_client(self, client_type: type[ClientTypes]) -> ClientTypes:
        return client_type(timeout=self.settings.timeout.total_seconds(), http2=True)

    async def get_async_client(self) -> httpx.AsyncClient:
        if self.__async_client is None:
            self.__async_client = cast(httpx.AsyncClient, self.__create_client(httpx.AsyncClient))
        return self.__async_client

    def get_sync_client(self) -> httpx.Client:
        if self.__sync_client is None:
            self.__sync_client = cast(httpx.Client, self.__create_client(httpx.Client))
        return self.__sync_client

    async def _async_send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = await (await self.get_async_client()).post(
                    url.as_string(), content=data, headers=self._json_headers()
                )
                data_received = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.TimeoutException:
                last_exception = self._construct_timeout_exception(url, data, stopwatch.lap)
            except httpx.ConnectError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except httpx.HTTPError as error:
                last_exception = error
            await self._async_sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception

    def _send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = self.get_sync_client().post(
                    url.as_string(), content=data, headers=self._json_headers()
                )
                data_received = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.TimeoutException:
                last_exception = self._construct_timeout_exception(url, data, stopwatch.lap)
            except httpx.ConnectError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except httpx.HTTPError as error:
                last_exception = error
            self._sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception
