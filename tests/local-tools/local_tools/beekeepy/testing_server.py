from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from http import HTTPStatus
from threading import Thread
from typing import TYPE_CHECKING

from aiohttp import web

from beekeepy.interfaces import HttpUrl, SelfContextAsync

if TYPE_CHECKING:
    from socket import socket
    from typing import Any, Iterator

    from typing_extensions import Self


class AsyncHttpServerError(Exception):
    pass


class ServerNotRunningError(AsyncHttpServerError):
    def __init__(self) -> None:
        super().__init__("Server is not running. Call run() first.")


class ServerAlreadyRunningError(AsyncHttpServerError):
    def __init__(self) -> None:
        super().__init__("Server is already running. Call close() first.")


class ServerSetupError(AsyncHttpServerError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class HttpServerObserver(ABC):
    @abstractmethod
    async def data_received(self, data: dict[str, Any]) -> None:
        """Called when any data is received via PUT method.

        Args:
            data: data received as body

        Returns:
            Nothing.
        """


class AsyncHttpServer(SelfContextAsync):
    __ADDRESS = HttpUrl("0.0.0.0:0")

    def __init__(self, observer: HttpServerObserver, notification_endpoint: HttpUrl | None) -> None:
        self.__observer = observer
        self._app = web.Application()
        self.__site: web.TCPSite | None = None
        self.__running: bool = False
        self.__notification_endpoint = notification_endpoint
        self._setup_routes()

    def _setup_routes(self) -> None:
        async def handle_put_method(request: web.Request) -> web.Response:
            await self.__observer.data_received(await request.json())
            return web.Response(status=HTTPStatus.NO_CONTENT)

        self._app.router.add_route("PUT", "/", handle_put_method)

    @property
    def port(self) -> int:
        if not self.__site:
            raise ServerNotRunningError
        server: asyncio.base_events.Server | None = self.__site._server  # type: ignore[assignment]
        if server is None:
            raise ServerSetupError("self.__site.server is None")

        server_socket: socket = server.sockets[0]
        address_tuple: tuple[str, int] = server_socket.getsockname()

        if not (
            isinstance(address_tuple, tuple) and isinstance(address_tuple[0], str) and isinstance(address_tuple[1], int)
        ):
            raise ServerSetupError(f"address_tuple has not recognizable types: {address_tuple}")

        return address_tuple[1]

    async def run(self) -> None:
        if self.__site:
            raise ServerAlreadyRunningError

        time_between_checks_is_server_running = 0.5

        runner = web.AppRunner(self._app, access_log=False)
        await runner.setup()
        address = self.__notification_endpoint or self.__ADDRESS
        self.__site = web.TCPSite(runner, address.address, address.port)
        await self.__site.start()
        self.__running = True
        try:
            while self.__running:  # noqa: ASYNC110
                await asyncio.sleep(time_between_checks_is_server_running)
        finally:
            await self.__site.stop()
            self.__site = None

    def close(self) -> None:
        if not self.__site:
            raise ServerNotRunningError
        self.__running = False

    async def _aenter(self) -> Self:
        await self.run()
        return self

    async def _afinally(self) -> None:
        self.close()


class DummyObserver(HttpServerObserver):
    async def data_received(self, data: dict[str, Any]) -> None:  # noqa: ARG002
        return None


class TestAsyncHttpServer(AsyncHttpServer):
    def __init__(self, response: str) -> None:
        self.__response = response
        super().__init__(DummyObserver(), None)

    def _setup_routes(self) -> None:
        async def handle_post_method(request: web.Request) -> web.Response:  # noqa: ARG001
            return web.Response(text=self.__response)

        self._app.router.add_route("POST", "/", handle_post_method)


def create_simple_server(response: str) -> TestAsyncHttpServer:
    return TestAsyncHttpServer(response=response)


@contextmanager
def run_simple_server(response: str) -> Iterator[HttpUrl]:
    server = create_simple_server(response)

    worker = Thread(target=asyncio.run, args=(server.run(),))
    worker.start()
    time.sleep(0.5)

    try:
        yield HttpUrl(f"http://127.0.0.1:{server.port}")
    finally:
        server.close()
        worker.join()
