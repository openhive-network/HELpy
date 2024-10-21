from __future__ import annotations

from helpy import HttpUrl, WsUrl
from helpy._interfaces.config import Config

from pathlib import Path
from pydantic import Field

def http_webserver_default() -> HttpUrl:
    return HttpUrl("0.0.0.0:0")


# All config items are automatically generated
class BeekeeperCommon(Config):
    # Whether to print backtrace on SIGSEGV
    backtrace: str = "yes"

    # json-rpc log directory name.
    log_json_rpc: str | None = None

    # list of addresses, that will receive notification about in-chain events
    notifications_endpoint: list[HttpUrl] = []

    # Plugin(s) to enable, may be specified multiple times
    plugin: list[str] = []

    # Protection against unlocking by bots. Every wrong `unlock` enables a delay. By default 500[ms].
    unlock_interval: int = 500

    # Timeout for unlocked wallet in seconds (default 900 (15 minutes)).Wallets will be automatically locked after specified number of seconds of inactivity.Activity is defined as any wallet command e.g. list-wallets.
    unlock_timeout: int = 900

    # The path of the wallet files (absolute path or relative to application data dir)
    wallet_dir: Path = Field(default_factory=lambda: Path("."))

    # Local http endpoint for webserver requests.
    webserver_http_endpoint: HttpUrl | None = None

    # File name with a server's certificate.
    webserver_https_certificate_file_name: str | None = None

    # Local https endpoint for webserver requests.
    webserver_https_endpoint: HttpUrl | None = None

    # File name with a server's private key.
    webserver_https_key_file_name: str | None = None

    # Number of threads used to handle queries. Default: 32.
    webserver_thread_pool_size: int = 32

    # Local unix http endpoint for webserver requests.
    webserver_unix_endpoint: HttpUrl | None = None

    # Enable the RFC-7692 permessage-deflate extension for the WebSocket server (only used if the client requests it).  This may save bandwidth at the expense of CPU
    webserver_ws_deflate: bool = False

    # Local websocket endpoint for webserver requests.
    webserver_ws_endpoint: WsUrl | None = None
