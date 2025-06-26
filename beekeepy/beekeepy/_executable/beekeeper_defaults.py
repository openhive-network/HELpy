from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from msgspec import field

from beekeepy._communication import HttpUrl, P2PUrl, WsUrl  # noqa: TCH001
from beekeepy._executable.beekeeper_custom_parameters_types import ExportKeysWalletParams  # noqa: TCH001
from schemas._preconfigured_base_model import PreconfiguredBaseModel


class BeekeeperDefaults(PreconfiguredBaseModel):
    DEFAULT_BACKTRACE: ClassVar[str] = "yes"
    DEFAULT_LOG_JSON_RPC: ClassVar[Path | None] = None
    DEFAULT_PLUGIN: ClassVar[list[str]] = []
    DEFAULT_UNLOCK_INTERVAL: ClassVar[int] = 500
    DEFAULT_UNLOCK_TIMEOUT: ClassVar[int] = 900
    DEFAULT_WALLET_DIR: ClassVar[Path] = field(default_factory=lambda: Path())
    DEFAULT_WEBSERVER_HTTP_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_HTTPS_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_THREAD_POOL_SIZE: ClassVar[int] = 32
    DEFAULT_WEBSERVER_UNIX_ENDPOINT: ClassVar[P2PUrl | None] = None
    DEFAULT_WEBSERVER_WS_DEFLATE: ClassVar[bool] = False
    DEFAULT_WEBSERVER_WS_ENDPOINT: ClassVar[WsUrl | None] = None
    DEFAULT_CONFIG: ClassVar[Path] = field(default_factory=lambda: Path("config.ini"))
    DEFAULT_DATA_DIR: ClassVar[Path | None] = None
    DEFAULT_DUMP_CONFIG: ClassVar[bool] = False
    DEFAULT_DUMP_OPTIONS: ClassVar[bool] = False
    DEFAULT_EXPORT_KEYS_WALLET: ClassVar[list[ExportKeysWalletParams]] = []
    DEFAULT_GENERATE_COMPLETIONS: ClassVar[bool] = False
    DEFAULT_HELP_: ClassVar[bool] = False
    DEFAULT_LIST_PLUGINS: ClassVar[bool] = False
    DEFAULT_VERSION_: ClassVar[bool] = False
