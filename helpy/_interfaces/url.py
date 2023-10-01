from __future__ import annotations

from typing import Generic, Literal, TypeVar
from urllib.parse import urlparse

P2PProtocolT = Literal[""]
HttpProtocolT = Literal["http", "https"]
WsProtocolT = Literal["ws", "wss"]
ProtocolT = TypeVar("ProtocolT", bound=HttpProtocolT | WsProtocolT | P2PProtocolT)


class Url(Generic[ProtocolT]):
    """Wrapper for Url, for handy access to all of it members with serialization."""

    def __init__(self, url: str | Url[ProtocolT], *, protocol: ProtocolT = "") -> None:  # type: ignore[assignment]
        if isinstance(url, Url):
            self.__protocol: str = url.__protocol
            self.__address: str = url.__address
            self.__port: int | None = url.__port
        elif isinstance(url, str):
            parsed_url = urlparse(url, scheme=protocol)
            if not parsed_url.netloc:
                parsed_url = urlparse(f"//{url}", scheme=protocol)

            if not parsed_url.hostname:
                raise ValueError("Address was not specified.")

            self.__protocol = parsed_url.scheme
            self.__address = parsed_url.hostname
            self.__port = parsed_url.port
        else:
            raise TypeError("Unknown type, cannot convert to Url")

    @property
    def protocol(self) -> ProtocolT:
        """Return protocol of url, e.x: http, https."""
        return self.__protocol  # type: ignore[return-value]

    @property
    def address(self) -> str:
        """Return address or hostname of url, e.x: 127.0.0.1, localhost."""
        return self.__address

    @property
    def port(self) -> int | None:
        """Return port of url, e.x: 0, 8090."""
        return self.__port

    def as_string(self, *, with_protocol: bool = True) -> str:
        """Serializes url."""
        protocol_prefix = f"{self.protocol}://" if with_protocol else ""
        port_suffix = f":{self.port}" if self.port else ""

        return f"{protocol_prefix}{self.address}{port_suffix}"


HttpUrl = Url[HttpProtocolT]
WsUrl = Url[WsProtocolT]
P2PUrl = Url[P2PProtocolT]
AnyUrl = Url[HttpProtocolT] | Url[WsProtocolT] | Url[P2PProtocolT]
