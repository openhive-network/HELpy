from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar, cast

import helpy
from beekeepy._executable import BeekeeperArguments, BeekeeperExecutable
from beekeepy._executable.arguments.beekeeper_arguments import BeekeeperArgumentsDefaults
from beekeepy._interface.settings import Settings
from beekeepy.exceptions import BeekeeperAlreadyRunningError, BeekeeperIsNotRunningError
from helpy import ContextAsync, ContextSync

if TYPE_CHECKING:
    from pathlib import Path

    from loguru import Logger

    from beekeepy._executable.beekeeper_config import BeekeeperConfig
    from helpy import KeyPair


EnterReturnT = TypeVar("EnterReturnT", bound=helpy.Beekeeper | helpy.AsyncBeekeeper)


__all__ = [
    "SyncRemoteBeekeeper",
    "AsyncRemoteBeekeeper",
    "Beekeeper",
    "AsyncBeekeeper",
]


class SyncRemoteBeekeeper(helpy.Beekeeper):
    pass


class AsyncRemoteBeekeeper(helpy.AsyncBeekeeper):
    pass


class BeekeeperCommon(ABC):
    def __init__(self, *args: Any, settings: Settings, logger: Logger, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__exec = BeekeeperExecutable(settings, logger)
        self.__logger = logger

    @property
    def pid(self) -> int:
        if not self.is_running:
            raise BeekeeperIsNotRunningError
        return self.__exec.pid

    @property
    def config(self) -> BeekeeperConfig:
        return self.__exec.config

    @property
    def is_running(self) -> bool:
        return self.__exec is not None and self.__exec.is_running()

    def __wait_till_ready(self) -> None:
        ports = self.__exec.reserved_ports()
        if False:
            raise NotImplementedError("TODO: Fix case when beekeeper is already running")
        raise TimeoutError("Waiting too long for beekeeper to be up and running")

    def _run(self, settings: Settings, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        aca = additional_cli_arguments or BeekeeperArguments()
        settings.http_endpoint = (
            aca.webserver_http_endpoint or settings.http_endpoint or helpy.HttpUrl("127.0.0.1:0", protocol="http")
        )
        settings.working_directory = (
            aca.data_dir
            if aca.data_dir != BeekeeperArgumentsDefaults.DEFAULT_DATA_DIR
            else self.__exec.working_directory
        )
        self._run_application(settings=settings, additional_cli_arguments=aca)
        try:
            self.__wait_till_ready()
        except BeekeeperAlreadyRunningError:
            self.close()
            raise

    def _run_application(self, settings: Settings, additional_cli_arguments: BeekeeperArguments) -> None:
        assert settings.http_endpoint is not None
        self.__exec.run(
            blocking=False,
            arguments=additional_cli_arguments.copy(
                update={
                    "webserver_http_endpoint": settings.http_endpoint,
                    "data_dir": settings.working_directory,
                }
            ),
            propagate_sigint=settings.propagate_sigint,
        )

    def detach(self) -> None:
        self.__exec.detach()

    def close(self) -> None:
        self._close_application()

    def _close_application(self) -> None:
        if self.__exec.is_running():
            self.__exec.close(self._get_settings().close_timeout.total_seconds())

    def export_keys_wallet(
        self, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> list[KeyPair]:
        return self.__exec.export_keys_wallet(
            wallet_name=wallet_name, wallet_password=wallet_password, extract_to=extract_to
        )

    @abstractmethod
    def _get_settings(self) -> Settings: ...


class Beekeeper(BeekeeperCommon, SyncRemoteBeekeeper, ContextSync["Beekeeper"]):
    def run(self, *, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        self._clear_session()
        with self.update_settings() as settings:
            self._run(settings=cast(Settings, settings), additional_cli_arguments=additional_cli_arguments)
        self.http_endpoint = self._get_http_endpoint_from_event()

    def _get_settings(self) -> Settings:
        assert isinstance(self.settings, Settings)
        return self.settings

    @property
    def settings(self) -> Settings:
        return cast(Settings, super().settings)

    def _enter(self) -> Beekeeper:
        self.run()
        return self

    def _finally(self) -> None:
        self.close()


class AsyncBeekeeper(BeekeeperCommon, AsyncRemoteBeekeeper, ContextAsync["AsyncBeekeeper"]):
    def run(self, *, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        self._clear_session()
        with self.update_settings() as settings:
            self._run(settings=cast(Settings, settings), additional_cli_arguments=additional_cli_arguments)
        self.http_endpoint = self._get_http_endpoint_from_event()

    def _get_settings(self) -> Settings:
        assert isinstance(self.settings, Settings)
        return self.settings

    @property
    def settings(self) -> Settings:
        return cast(Settings, super().settings)

    async def _aenter(self) -> AsyncBeekeeper:
        self.run()
        return self

    async def _afinally(self) -> None:
        self.close()
