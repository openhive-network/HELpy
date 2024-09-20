from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass, field

from helpy import HttpUrl, P2PUrl, WsUrl

__all__ = ["PortMatchingResult", "match_ports"]


@dataclass
class PortMatchingResult:
    http: HttpUrl | None = None
    https: HttpUrl | None = None
    websocket: WsUrl | None = None
    p2p: list[P2PUrl] = field(default_factory=list)


def test_http(address: HttpUrl) -> bool:
    assert address.port is not None, "HTTP CHECK: Port has to be set"
    try:
        with socket.create_connection((address.address, address.port), timeout=1) as sock:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = sock.recv(1024).decode("utf-8")
            return response.startswith("HTTP")
    except (OSError, socket.timeout, ConnectionRefusedError):
        return False


def test_https(address: HttpUrl) -> bool:
    assert address.port is not None, "HTTPS CHECK: Port has to be set"
    try:
        context = ssl.create_default_context()
        with socket.create_connection((address.address, address.port), timeout=1) as sock, context.wrap_socket(
            sock, server_hostname="localhost"
        ) as ssock:
            ssock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = ssock.recv(1024).decode("utf-8")
            return response.startswith("HTTP")
    except (OSError, socket.timeout, ConnectionRefusedError, ssl.SSLError):
        return False


def test_websocket(address: WsUrl) -> bool:
    assert address.port is not None, "WS CHECK: Port has to be set"
    try:
        with socket.create_connection((address.address, address.port), timeout=1) as sock:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
            response = sock.recv(1024).decode("utf-8")
            return "101 Switching Protocols" in response
    except (OSError, socket.timeout, ConnectionRefusedError):
        return False


def match_ports(ports: list[int], *, address: str = "127.0.0.1") -> PortMatchingResult:
    categories = PortMatchingResult()
    for port in ports:
        if categories.http is None and test_http(http_result := HttpUrl.factory(port=port, address=address)):
            categories.http = http_result
        elif categories.https is None and test_https(http_result := HttpUrl.factory(port=port, address=address)):
            categories.https = http_result
        elif categories.websocket is None and test_websocket(ws_result := WsUrl.factory(port=port, address=address)):
            categories.websocket = ws_result
        else:
            categories.p2p.append(P2PUrl.factory(port=port, address=address))

    return categories
