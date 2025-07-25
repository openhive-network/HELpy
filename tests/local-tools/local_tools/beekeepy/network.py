from __future__ import annotations

import socket
from json import loads
from typing import TYPE_CHECKING, Any

from beekeepy._communication import get_communicator_cls
from beekeepy.handle.remote import RemoteHandleSettings

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl
    from schemas.jsonrpc import JSONRPCRequest


async def async_raw_http_call(*, http_endpoint: HttpUrl, data: JSONRPCRequest) -> dict[str, Any]:
    """Make raw call with given data to given http_endpoint."""
    communicator = get_communicator_cls("aiohttp")(settings=RemoteHandleSettings(http_endpoint=http_endpoint))
    response = await communicator.async_post(url=http_endpoint, data=data.json())
    parsed = loads(response)
    assert isinstance(parsed, dict), "expected json object"
    return parsed


def raw_http_call(*, http_endpoint: HttpUrl, data: JSONRPCRequest) -> dict[str, Any]:
    """Make raw call with given data to given http_endpoint."""
    communicator = get_communicator_cls("request")(settings=RemoteHandleSettings(http_endpoint=http_endpoint))
    response = communicator.post(url=http_endpoint, data=data.json())
    parsed = loads(response)
    assert isinstance(parsed, dict), "expected json object"
    return parsed


def get_port() -> int:
    """Return free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return int(sock.getsockname()[1])
