from __future__ import annotations

import asyncio
import time
from contextlib import contextmanager
from threading import Thread
from typing import Any, Iterator

from aiohttp import web

from beekeepy._communication.abc.http_server_observer import HttpServerObserver
from beekeepy.handle.runnable import AsyncHttpServer
from beekeepy.interfaces import HttpUrl


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
