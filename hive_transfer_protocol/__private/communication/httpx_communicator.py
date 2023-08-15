from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import httpx

from hive_transfer_protocol.__private.communication.abc.communicator import (
    AbstractCommunicator,
    CommunicationError,
)

if TYPE_CHECKING:
    from hive_transfer_protocol.__private.interfaces.url import HttpUrl


class HttpxCommunicator(AbstractCommunicator):
    """Provides support for httpx library."""

    __async_client: ClassVar[httpx.AsyncClient | None] = None

    @classmethod
    def start(cls) -> None:
        if cls.__async_client is None:
            cls.__async_client = httpx.AsyncClient(timeout=cls.timeout.total_seconds(), http2=True)

    @classmethod
    async def close(cls) -> None:
        if cls.__async_client is not None:
            await cls.__async_client.aclose()
            cls.__async_client = None

    @classmethod
    def get_async_client(cls) -> httpx.AsyncClient:
        assert cls.__async_client is not None, "Session is closed."
        return cls.__async_client

    @classmethod
    async def async_send(cls, url: HttpUrl, data: str) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while cls._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = await cls.get_async_client().post(
                    url.as_string(), content=data, headers=cls._json_headers()
                )
                data_received = response.content.decode()
                cls._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.ConnectError as error:
                raise CommunicationError(url, data) from error
            except httpx.HTTPError as error:
                last_exception = error
            await cls._async_sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception

    @classmethod
    def send(cls, url: HttpUrl, data: str) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while cls._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: httpx.Response = httpx.post(url.as_string(), content=data, headers=cls._json_headers())
                data_received = response.content.decode()
                cls._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except httpx.ConnectError as error:
                raise CommunicationError(url, data) from error
            except httpx.HTTPError as error:
                last_exception = error
            cls._sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception
