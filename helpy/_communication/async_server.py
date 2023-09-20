from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import TYPE_CHECKING

from aiohttp import web
from typing_extensions import Self

from helpy._interfaces.context import ContextAsync
from helpy.exceptions import HelpyError

if TYPE_CHECKING:
    from socket import socket

    from helpy._communication.abc.http_server_observer import HttpServerObserver


class AsyncHttpServerError(HelpyError):
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


class AsyncHttpServer(ContextAsync[Self]):  # type: ignore[misc]
    __ADDRESS = ("0.0.0.0", 0)

    def __init__(self, observer: HttpServerObserver) -> None:
        self.__observer = observer
        self.__app = web.Application()
        self.__site: web.TCPSite | None = None
        self.__running: bool = False

        async def handle_put_method(request: web.Request) -> web.Response:
            await self.__observer.data_received(await request.json())
            return web.Response(status=HTTPStatus.NO_CONTENT)

        self.__app.router.add_route("PUT", "/", handle_put_method)

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

        runner = web.AppRunner(self.__app)
        await runner.setup()
        self.__site = web.TCPSite(runner, *self.__ADDRESS)
        await self.__site.start()
        self.__running = True
        try:
            while self.__running:
                await asyncio.sleep(time_between_checks_is_server_running)
        finally:
            await self.__site.stop()
            self.__site = None

    def close(self) -> None:
        if not self.__site:
            raise ServerNotRunningError
        self.__running = False

    async def _enter(self) -> Self:
        await self.run()
        return self

    async def _finally(self) -> None:
        self.close()
