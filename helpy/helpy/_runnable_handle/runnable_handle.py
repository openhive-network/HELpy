from __future__ import annotations

import time
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from loguru import logger as default_logger

from helpy._executable.executable import ArgumentT, ConfigT, Executable
from helpy._interfaces.url import HttpUrl
from helpy._runnable_handle.match_ports import PortMatchingResult, match_ports
from helpy._runnable_handle.settings import Settings

if TYPE_CHECKING:
    from loguru import Logger


ExecutableT = TypeVar("ExecutableT", bound=Executable[Any, Any])
SettingsT = TypeVar("SettingsT", bound=Settings)
T = TypeVar("T")


class RunnableHandle(ABC, Generic[ExecutableT, ConfigT, ArgumentT, SettingsT]):
    def __init__(self, *args: Any, logger: Logger | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger or default_logger
        self._exec = self._construct_executable()

    @property
    def pid(self) -> int:
        """Returns pid of started executable. Note: Proxy method to Executable.pid."""
        return self._exec.pid

    @property
    def arguments(self) -> ArgumentT:
        """Returns arguments for given binary. Note: Proxy method to Executable.arguments."""
        return cast(ArgumentT, self._exec.arguments)

    @property
    def config(self) -> ConfigT:
        """Returns config for given binary. Note: Proxy method to Executable.config."""
        return cast(ConfigT, self._exec.config)

    @property
    def is_running(self) -> bool:
        """Returns is process running. Note: Proxy method to Executable.is_running."""
        return self._exec.is_running()

    def detach(self) -> None:
        """Detaches process and allows to keep it after closing python script."""
        self._exec.detach()

    def close(self) -> None:
        """Closes running process. If process is not running, method does nothing."""
        if self.is_running:
            self._exec.close(timeout_secs=self._get_settings().close_timeout.total_seconds())

    def get_help_text(self) -> str:
        """Returns help printed by executable."""
        self.__show_warning_if_executable_already_running()
        return self._exec.get_help_text()

    def get_version(self) -> str:
        """Returns version string printed by executable."""
        self.__show_warning_if_executable_already_running()
        return self._exec.version()

    def generate_default_config_from_executable(self) -> ConfigT:
        """Returns config generated by executable."""
        self.__show_warning_if_executable_already_running()
        return cast(ConfigT, self._exec.generate_default_config())

    def _run(self, *, environment_variables: dict[str, str] | None = None, perform_unification: bool = True) -> None:
        """
        Runs executable and unifies arguments.

        Note: This method should be called by RunnableHandleChild.run, which is not defined by this interface!

        Keyword Arguments:
            environment_variables -- additional environment variables to set before launching executable
            additional_cli_arguments -- arguments to add to executable invocation
            perform_unification -- if set to true, chosen values will be written to config and cli arguments
        """
        settings = self._get_settings().copy()

        settings.working_directory = self.__choose_working_directory(settings=settings)
        settings.http_endpoint = self.__choose_http_endpoint(settings=settings)
        if perform_unification:
            self._unify_cli_arguments(settings.working_directory, settings.http_endpoint)
            self._unify_config(settings.working_directory, settings.http_endpoint)

        self._exec.run(blocking=False, environ=environment_variables, propagate_sigint=settings.propagate_sigint)
        self._wait_for_app_to_start()
        self._setup_ports(match_ports(self._exec.reserved_ports()))

    @abstractmethod
    def _construct_executable(self) -> ExecutableT:
        """Returns executable instance."""

    @abstractmethod
    def _get_settings(self) -> SettingsT:
        """Returns settings hold by child class. Used only for read-only purposes."""

    def _get_working_directory_from_cli_arguments(self) -> Path | None:
        """Returns working directory from specified cli arguments in executable (if specified)."""
        return None

    def _get_http_endpoint_from_cli_arguments(self) -> HttpUrl | None:
        """Returns http endpoint from specified cli arguments in executable (if specified)."""
        return None

    def _get_working_directory_from_config(self) -> Path | None:
        """Returns working directory from specified config in executable (if specified)."""
        return None

    def _get_http_endpoint_from_config(self) -> HttpUrl | None:
        """Returns http endpoint from specified config in executable (if specified)."""
        return None

    @abstractmethod
    def _unify_cli_arguments(self, working_directory: Path, http_endpoint: HttpUrl) -> None:
        """
        Writes selected values to given cli arguments and returns it.

        Args:
            working_directory -- chosen working path to be set in cli arguments.
            http_endpoint -- chosen http endpoint to be set in cli arguments.
        """

    @abstractmethod
    def _unify_config(self, working_directory: Path, http_endpoint: HttpUrl) -> None:
        """
        Writes selected values to config in executable.

        Args:
            working_directory -- chosen working path to be set in config.
            http_endpoint -- chosen http endpoint to be set in config.
        """

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        """
        Setup ports after startup.

        Args:
            ports -- list of ports reserved by started application.
        """

    def _wait_for_app_to_start(self) -> None:
        """Waits for application to start."""
        while not self._exec.reserved_ports():
            time.sleep(0.1)

    def __choose_working_directory(self, settings: Settings) -> Path:
        return self.__choose_value(
            default_value=Path.cwd(),
            argument_value=self._get_working_directory_from_cli_arguments(),
            config_value=self._get_working_directory_from_config(),
            settings_value=settings.working_directory,
        )

    def __choose_http_endpoint(self, settings: Settings) -> HttpUrl:
        return self.__choose_value(
            default_value=HttpUrl("http://0.0.0.0:0"),
            argument_value=self._get_http_endpoint_from_cli_arguments(),
            config_value=self._get_http_endpoint_from_config(),
            settings_value=settings.http_endpoint,
        )

    def __show_warning_if_executable_already_running(self) -> None:
        if self.is_running:
            warnings.warn("Invoking executable that is already running!", stacklevel=2)

    @classmethod
    def __choose_value(
        cls,
        default_value: T,
        argument_value: T | None = None,
        config_value: T | None = None,
        settings_value: T | None = None,
    ) -> T:
        if argument_value is not None:
            return argument_value
        if config_value is not None:
            return config_value
        if settings_value is not None:
            return settings_value
        return default_value
