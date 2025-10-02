from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from beekeepy._executable.beekeeper_arguments import BeekeeperArguments
from beekeepy._executable.beekeeper_config import BeekeeperConfig
from beekeepy._executable.beekeeper_executable import BeekeeperExecutable
from beekeepy._runnable_handle.runnable_handle import RunnableHandle
from beekeepy._runnable_handle.settings import RunnableHandleSettings
from beekeepy.exceptions import BeekeeperFailedToStartError, ExecutableError

if TYPE_CHECKING:
    from pathlib import Path

    from beekeepy._communication.url import HttpUrl
    from beekeepy._runnable_handle.match_ports import PortMatchingResult
    from beekeepy._utilities.key_pair import KeyPair


RunnableSettingsT = TypeVar("RunnableSettingsT", bound=RunnableHandleSettings)


class RunnableBeekeeper(
    RunnableHandle[BeekeeperExecutable, BeekeeperConfig, BeekeeperArguments, RunnableHandleSettings]
):
    def _construct_executable(self) -> BeekeeperExecutable:
        settings = self._get_settings()
        return BeekeeperExecutable(
            executable_path=settings.binary_path,
            working_directory=settings.ensured_working_directory,
            logger=self._logger,
        )

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
            try:
                self._run()
            except ExecutableError as e:
                raise BeekeeperFailedToStartError from e

    def _write_ports(self, editable_settings: RunnableHandleSettings, ports: PortMatchingResult) -> None:
        editable_settings.http_endpoint = ports.http
        self.config.webserver_http_endpoint = ports.http
        self.config.webserver_ws_endpoint = ports.websocket

    def _close(self) -> None:
        self._close_application()

    def _close_application(self) -> None:
        if self._exec.is_running():
            self._exec.close(self._get_settings().close_timeout.total_seconds())

    def export_keys_wallet(
        self, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> list[KeyPair]:
        return self._exec.export_keys_wallet(
            wallet_name=wallet_name,
            wallet_password=wallet_password,
            extract_to=extract_to,
        )
