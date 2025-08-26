from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from beekeepy._communication.abc.communicator_models import Request, Response
    from beekeepy._communication.settings import CommunicationSettings


class AioHttpCommunicator(AbstractCommunicator):
    """Provides support for aiohttp library."""

    def __init__(self, *args: Any, settings: CommunicationSettings, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, **kwargs)
        self.__session: aiohttp.ClientSession | None = None

    @property
    async def session(self) -> aiohttp.ClientSession:
        if self.__session is None:
            self.__session = aiohttp.ClientSession()
        return self.__session

    async def _async_send(self, request: Request) -> Response:
        """Sends to given url given data asynchronously."""
        try:
            async with (await self.session).request(
                method=request.method,
                url=request.url.as_string(),
                data=self._encode_data(request.body) if request.body is not None else None,
                headers=request.headers,
                timeout=aiohttp.ClientTimeout(total=request.get_timeout()),
            ) as response:
                return self._prepare_response(
                    status_code=response.status, headers=dict(response.headers), response=await response.text()
                )
        except (aiohttp.ServerTimeoutError, asyncio.TimeoutError) as error:
            raise self._construct_timeout_exception(request) from error
        except aiohttp.ClientError as error:
            raise CommunicationError(url=request.url, request=request.body or "") from error

    def _send(self, request: Request) -> Response:
        raise NotImplementedError

    def teardown(self) -> None:
        if self.__session is not None:
            self._asyncio_run(self.__session.close())
