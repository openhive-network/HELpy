from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from beekeepy._communication.abc.communicator_models import Request, Response
    from beekeepy._communication.settings import CommunicationSettings

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
        return client_type(http2=True)

    async def get_async_client(self) -> httpx.AsyncClient:
        if self.__async_client is None:
            self.__async_client = cast(httpx.AsyncClient, self.__create_client(httpx.AsyncClient))
        return self.__async_client

    def get_sync_client(self) -> httpx.Client:
        if self.__sync_client is None:
            self.__sync_client = cast(httpx.Client, self.__create_client(httpx.Client))
        return self.__sync_client

    async def _async_send(self, request: Request) -> Response:
        """Sends to given url given data asynchronously."""
        try:
            response: httpx.Response = await (await self.get_async_client()).request(
                method=request.method,
                url=request.url.as_string(),
                content=request.body,
                headers=request.headers,
                timeout=request.get_timeout(),
            )
            return self._prepare_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                response=self._decode_data(response.content),
            )
        except httpx.TimeoutException as error:
            raise self._construct_timeout_exception(request) from error
        except httpx.ConnectError as error:
            raise CommunicationError(url=request.url, request=request.body or "") from error

    def _send(self, request: Request) -> Response:
        """Sends to given url given data synchronously."""
        try:
            response: httpx.Response = self.get_sync_client().request(
                method=request.method,
                url=request.url.as_string(),
                content=self._encode_data(request.body) if request.body is not None else None,
                headers=request.headers,
                timeout=self.settings.timeout.total_seconds(),
            )
            return self._prepare_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                response=self._decode_data(response.content),
            )
        except httpx.TimeoutException as error:
            raise self._construct_timeout_exception(request) from error
        except httpx.ConnectError as error:
            raise CommunicationError(url=request.url, request=request.body or "") from error
