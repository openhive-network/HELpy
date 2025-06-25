from __future__ import annotations

from pathlib import Path  # noqa: TCH003

from beekeepy._communication import HttpUrl, WsUrl  # noqa: TCH001
from beekeepy._executable.beekeeper_defaults import BeekeeperDefaults
from schemas._preconfigured_base_model import PreconfiguredBaseModel


# All config items are automatically generated
class BeekeeperCommon(PreconfiguredBaseModel):
    """Parameters used in command line and in config file."""

    backtrace: str = BeekeeperDefaults.DEFAULT_BACKTRACE
    """Whether to print backtrace on SIGSEGV"""

    log_json_rpc: Path | None = BeekeeperDefaults.DEFAULT_LOG_JSON_RPC
    """json-rpc log directory name."""

    plugin: list[str] = BeekeeperDefaults.DEFAULT_PLUGIN
    """Plugin(s) to enable, may be specified multiple times"""

    unlock_interval: int = BeekeeperDefaults.DEFAULT_UNLOCK_INTERVAL
    """Protection against unlocking by bots. Every wrong `unlock` enables a delay. By default 500[ms]."""

    unlock_timeout: int = BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT
    """Timeout for unlocked wallet in seconds (default 900 (15 minutes)).Wallets will be automatically locked after
number of seconds of inactivity.Activity is defined as any wallet command e.g. list-wallets.
"""

    wallet_dir: Path = BeekeeperDefaults.DEFAULT_WALLET_DIR
    """The path of the wallet files (absolute path or relative to application data dir)"""

    webserver_http_endpoint: HttpUrl | None = BeekeeperDefaults.DEFAULT_WEBSERVER_HTTP_ENDPOINT
    """Local http endpoint for webserver requests."""

    webserver_https_certificate_file_name: str | None = BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME
    """File name with a server's certificate."""

    webserver_https_endpoint: HttpUrl | None = BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_ENDPOINT
    """Local https endpoint for webserver requests."""

    webserver_https_key_file_name: str | None = BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME
    """File name with a server's private key."""

    webserver_thread_pool_size: int = BeekeeperDefaults.DEFAULT_WEBSERVER_THREAD_POOL_SIZE
    """Number of threads used to handle queries. Default: 32."""

    webserver_unix_endpoint: HttpUrl | None = BeekeeperDefaults.DEFAULT_WEBSERVER_UNIX_ENDPOINT
    """Local unix http endpoint for webserver requests."""

    webserver_ws_deflate: bool = BeekeeperDefaults.DEFAULT_WEBSERVER_WS_DEFLATE
    """Enable the RFC-7692 permessage-deflate extension for the WebSocket server (only used if the client requests it).
This may save bandwidth at the expense of CPU
"""

    webserver_ws_endpoint: WsUrl | None = BeekeeperDefaults.DEFAULT_WEBSERVER_WS_ENDPOINT
    """Local websocket endpoint for webserver requests."""
