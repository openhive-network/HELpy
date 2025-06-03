from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Final

from beekeepy._communication import HttpUrl, P2PUrl, WsUrl

__all__ = ["PortMatchingResult", "match_ports"]

# https://http.cat/status/426
WEBSERVER_SPECIFIC_RESPONSE: Final[bytes] = b"426 Upgrade Required"


@dataclass
class PortMatchingResult:
    http: HttpUrl | None = None
    https: HttpUrl | None = None
    websocket: WsUrl | None = None
    p2p: list[P2PUrl] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.http is not None


def verify_is_http_endpoint(address: HttpUrl) -> bool:
    assert address.port is not None, "HTTP CHECK: Port has to be set"
    from beekeepy._remote_handle import AppStatusProbe, RemoteHandleSettings
    from beekeepy.exceptions import CommunicationError

    try:
        AppStatusProbe(
            settings=RemoteHandleSettings(
                http_endpoint=address,
                max_retries=0,
                period_between_retries=timedelta(seconds=0),
                timeout=timedelta(microseconds=300),
            )
        ).api.get_app_status()
    except CommunicationError:
        return False
    return True


def verify_is_https_endpoint(address: HttpUrl) -> bool:
    assert address.port is not None, "HTTPS CHECK: Port has to be set"
    try:
        context = ssl.create_default_context()
        with socket.create_connection((address.address, address.port), timeout=1) as sock, context.wrap_socket(
            sock, server_hostname="localhost"
        ) as ssl_sock:
            ssl_sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = ssl_sock.recv(1024)
            return response.startswith(b"HTTP") and WEBSERVER_SPECIFIC_RESPONSE not in response
    except (OSError, socket.timeout, ConnectionRefusedError, ssl.SSLError):
        return False


def verify_is_websocket_endpoint(address: WsUrl) -> bool:
    assert address.port is not None, "WS CHECK: Port has to be set"
    try:
        with socket.create_connection((address.address, address.port), timeout=1) as sock:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
            response = sock.recv(1024)
            return WEBSERVER_SPECIFIC_RESPONSE in response
    except (OSError, socket.timeout, ConnectionRefusedError):
        return False


def match_ports(ports: list[int], *, address: str = "127.0.0.1") -> PortMatchingResult:
    categories = PortMatchingResult()
    for port in ports:
        http_result = HttpUrl.factory(port=port, address=address)
        if categories.http is None and verify_is_http_endpoint(http_result):
            categories.http = http_result
        elif categories.https is None and verify_is_https_endpoint(http_result):
            categories.https = http_result
        elif categories.websocket is None and verify_is_websocket_endpoint(
            ws_result := WsUrl.factory(port=port, address=address)
        ):
            categories.websocket = ws_result
        else:
            categories.p2p.append(P2PUrl.factory(port=port, address=address))

    return categories
