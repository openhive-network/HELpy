from __future__ import annotations

from typing import Final

from helpy import HttpUrl, WsUrl

URL_TYPES = type[HttpUrl] | type[WsUrl]


DEFAULT_ADDRESS: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 8080
