from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

import helpy
from beekeepy._executable import BeekeeperArguments, BeekeeperExecutable
from beekeepy._executable.beekeeper_config import BeekeeperConfig
from beekeepy._interface.settings import Settings
from helpy import ContextAsync, ContextSync, HttpUrl, KeyPair
from helpy._runnable_handle.runnable_handle import RunnableHandle

if TYPE_CHECKING:
    from pathlib import Path

    from helpy._runnable_handle.match_ports import PortMatchingResult


__all__ = [
    "SyncRemoteBeekeeper",
    "AsyncRemoteBeekeeper",
    "Beekeeper",
    "AsyncBeekeeper",
]


class SyncRemoteBeekeeper(helpy.SyncBeekeeperTemplate[Settings]):
    pass


class AsyncRemoteBeekeeper(helpy.AsyncBeekeeperTemplate[Settings]):
    pass


class RunnableBeekeeper(RunnableHandle[BeekeeperExecutable, BeekeeperConfig, BeekeeperArguments, Settings]):
    def _construct_executable(self) -> BeekeeperExecutable:
        return BeekeeperExecutable(settings=self._get_settings(), logger=self._logger)

    def _get_working_directory_from_cli_arguments(self) -> Path | None:
        return self.arguments.data_dir

    def _get_http_endpoint_from_cli_arguments(self) -> HttpUrl | None:
        return self.arguments.webserver_http_endpoint

    def _get_http_endpoint_from_config(self) -> HttpUrl | None:
        return self.config.webserver_http_endpoint

    def _unify_cli_arguments(self, working_directory: Path, http_endpoint: HttpUrl) -> None:
        self.arguments.data_dir = working_directory
        self.arguments.webserver_http_endpoint = http_endpoint

    def _unify_config(self, working_directory: Path, http_endpoint: HttpUrl) -> None:  # noqa: ARG002
        self.config.webserver_http_endpoint = http_endpoint

    def run(self, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        with self._exec.restore_arguments(additional_cli_arguments):
            self._pre_run_actions()
            self._run()

    def _write_ports(self, editable_settings: Settings, ports: PortMatchingResult) -> None:
        editable_settings.http_endpoint = ports.http

        self.config.webserver_http_endpoint = ports.http
        self.config.webserver_ws_endpoint = ports.websocket

    def export_keys_wallet(
        self, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> list[KeyPair]:
        return self._exec.export_keys_wallet(
            wallet_name=wallet_name, wallet_password=wallet_password, extract_to=extract_to
        )

    @abstractmethod
    def _pre_run_actions(self) -> None: ...


class Beekeeper(RunnableBeekeeper, SyncRemoteBeekeeper, ContextSync["Beekeeper"]):
    def _get_settings(self) -> Settings:
        return self.settings

    def _enter(self) -> Beekeeper:
        self.run()
        return self

    def _finally(self) -> None:
        self.close()

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        with self.update_settings() as settings:
            self._write_ports(settings, ports)

    def _pre_run_actions(self) -> None:
        self._clear_session()


class AsyncBeekeeper(RunnableBeekeeper, AsyncRemoteBeekeeper, ContextAsync["AsyncBeekeeper"]):
    def _get_settings(self) -> Settings:
        return self.settings

    async def _aenter(self) -> AsyncBeekeeper:
        self.run()
        return self

    async def _afinally(self) -> None:
        self.close()

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        with self.update_settings() as settings:
            self._write_ports(settings, ports)

    def _pre_run_actions(self) -> None:
        self._clear_session()
