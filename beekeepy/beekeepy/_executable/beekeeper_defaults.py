from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field

from beekeepy._executable.custom_parameters_types import ExportKeysWalletParams  # noqa: TCH001
from helpy import (  # noqa: TCH001
    HttpUrl,
    WsUrl,
)


class BeekeeperDefaults(BaseModel):
    DEFAULT_BACKTRACE: ClassVar[str] = "yes"
    DEFAULT_LOG_JSON_RPC: ClassVar[Path | None] = None
    DEFAULT_PLUGIN: ClassVar[list[str]] = Field(default_factory=list)
    DEFAULT_UNLOCK_INTERVAL: ClassVar[int] = 500
    DEFAULT_UNLOCK_TIMEOUT: ClassVar[int] = 900
    DEFAULT_WALLET_DIR: ClassVar[Path] = Field(default_factory=lambda: Path())
    DEFAULT_WEBSERVER_HTTP_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_HTTPS_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME: ClassVar[str | None] = None
    DEFAULT_WEBSERVER_THREAD_POOL_SIZE: ClassVar[int] = 32
    DEFAULT_WEBSERVER_UNIX_ENDPOINT: ClassVar[HttpUrl | None] = None
    DEFAULT_WEBSERVER_WS_DEFLATE: ClassVar[bool] = False
    DEFAULT_WEBSERVER_WS_ENDPOINT: ClassVar[WsUrl | None] = None
    DEFAULT_CONFIG: ClassVar[Path] = Field(default_factory=lambda: Path("config.ini"))
    DEFAULT_DATA_DIR: ClassVar[Path | None] = None
    DEFAULT_DUMP_CONFIG: ClassVar[bool] = False
    DEFAULT_DUMP_OPTIONS: ClassVar[bool] = False
    DEFAULT_EXPORT_KEYS_WALLET: ClassVar[list[ExportKeysWalletParams]] = []
    DEFAULT_GENERATE_COMPLETIONS: ClassVar[bool] = False
    DEFAULT_HELP: ClassVar[bool] = False
    DEFAULT_LIST_PLUGINS: ClassVar[bool] = False
    DEFAULT_VERSION: ClassVar[bool] = False
