from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any, TypeVar, cast

from beekeepy._communication.universal_notification_server import (
    UniversalNotificationServer,
)
from beekeepy._executable import BeekeeperArguments, BeekeeperExecutable
from beekeepy._executable.arguments.beekeeper_arguments import (
    BeekeeperArgumentsDefaults,
)
from beekeepy._interface.url import HttpUrl
from beekeepy._remote_handle import beekeeper as remote_beekeeper
from beekeepy._runnable_handle.beekeeper_callbacks import BeekeeperNotificationCallbacks
from beekeepy._runnable_handle.beekeeper_notification_handler import NotificationHandler
from beekeepy._runnable_handle.settings import Settings
from beekeepy.exceptions import (
    BeekeeperFailedToStartDuringProcessSpawnError,
    BeekeeperFailedToStartNotReadyOnTimeError,
    BeekeeperIsNotRunningError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from loguru import Logger

    from beekeepy._executable.beekeeper_config import BeekeeperConfig
    from beekeepy._interface.key_pair import KeyPair
    from schemas.notifications import (
        Error,
        Status,
        WebserverListeningNotification,
    )


EnterReturnT = TypeVar("EnterReturnT", bound=remote_beekeeper.Beekeeper | remote_beekeeper.AsyncBeekeeper)


__all__ = [
    "SyncRemoteBeekeeper",
    "AsyncRemoteBeekeeper",
    "Beekeeper",
    "AsyncBeekeeper",
]


class SyncRemoteBeekeeper(remote_beekeeper.Beekeeper):
    pass


class AsyncRemoteBeekeeper(remote_beekeeper.AsyncBeekeeper):
    pass


class BeekeeperCommon(BeekeeperNotificationCallbacks, ABC):
    def __init__(self, *args: Any, settings: Settings, logger: Logger, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, logger=logger, **kwargs)
        self.__exec = BeekeeperExecutable(settings, logger)
        self.__notification_server: UniversalNotificationServer | None = None
        self.__notification_event_handler: NotificationHandler | None = None
        self.__logger = logger

    @property
    def pid(self) -> int:
        if not self.is_running:
            raise BeekeeperIsNotRunningError
        return self.__exec.pid

    @property
    def notification_endpoint(self) -> HttpUrl:
        endpoint = self._get_settings().notification_endpoint
        assert endpoint is not None, "Notification endpoint is not set"
        return endpoint

    @property
    def config(self) -> BeekeeperConfig:
        return self.__exec.config

    @property
    def is_running(self) -> bool:
        return self.__exec is not None and self.__exec.is_running()

    def __setup_notification_server(self, *, address_from_cli_arguments: HttpUrl | None = None) -> None:
        assert self.__notification_server is None, "Notification server already exists, previous hasn't been close?"
        assert (
            self.__notification_event_handler is None
        ), "Notification event handler already exists, previous hasn't been close?"

        self.__notification_event_handler = NotificationHandler(self)
        self.__notification_server = UniversalNotificationServer(
            self.__notification_event_handler,
            notification_endpoint=address_from_cli_arguments
            or self._get_settings().notification_endpoint,  # this has to be accessed directly from settings
        )

    def __close_notification_server(self) -> None:
        if self.__notification_server is not None:
            self.__notification_server.close()
            self.__notification_server = None

        if self.__notification_event_handler is not None:
            self.__notification_event_handler = None

    def __wait_till_ready(self) -> None:
        assert self.__notification_event_handler is not None, "Notification event handler hasn't been set"
        if not self.__notification_event_handler.http_listening_event.wait(
            timeout=self._get_settings().initialization_timeout.total_seconds()
        ):
            raise TimeoutError("Waiting too long for beekeeper to be up and running")

    def _handle_error(self, error: Error) -> None:
        self.__logger.error(f"Beekeepr error: `{error.json()}`")

    def _handle_status_change(self, status: Status) -> None:
        self.__logger.info(f"Beekeeper status change to: `{status.current_status}`")

    def _run(
        self,
        settings: Settings,
        additional_cli_arguments: BeekeeperArguments | None = None,
    ) -> None:
        aca = additional_cli_arguments or BeekeeperArguments()
        self.__setup_notification_server(address_from_cli_arguments=aca.notifications_endpoint)
        assert self.__notification_server is not None, "Creation of notification server failed"
        settings.notification_endpoint = HttpUrl(f"127.0.0.1:{self.__notification_server.run()}", protocol="http")
        settings.http_endpoint = (
            aca.webserver_http_endpoint or settings.http_endpoint or HttpUrl("127.0.0.1:0", protocol="http")
        )
        settings.working_directory = (
            aca.data_dir
            if aca.data_dir != BeekeeperArgumentsDefaults.DEFAULT_DATA_DIR
            else self.__exec.working_directory
        )
        try:
            self._run_application(settings=settings, additional_cli_arguments=aca)
        except CalledProcessError as e:
            raise BeekeeperFailedToStartDuringProcessSpawnError from e
        try:
            self.__wait_till_ready()
        except (AssertionError, TimeoutError) as e:
            self._close()
            raise BeekeeperFailedToStartNotReadyOnTimeError from e

    def _run_application(self, settings: Settings, additional_cli_arguments: BeekeeperArguments) -> None:
        assert settings.notification_endpoint is not None
        assert settings.http_endpoint is not None
        assert settings.working_directory is not None
        additional_cli_arguments_copy = copy.deepcopy(additional_cli_arguments)
        additional_cli_arguments_copy.notifications_endpoint = settings.notification_endpoint
        additional_cli_arguments_copy.webserver_http_endpoint = settings.http_endpoint
        additional_cli_arguments_copy.data_dir = settings.working_directory
        self.__exec.run(
            blocking=False,
            arguments=additional_cli_arguments_copy,
            propagate_sigint=settings.propagate_sigint,
        )

    def detach(self) -> int:
        pid = self.__exec.detach()
        self.__close_notification_server()
        return pid

    def _close(self) -> None:
        self._close_application()
        self.__close_notification_server()

    def _close_application(self) -> None:
        if self.__exec.is_running():
            self.__exec.close(self._get_settings().close_timeout.total_seconds())

    def _http_webserver_ready(self, notification: WebserverListeningNotification) -> None:
        """It is converted by _get_http_endpoint_from_event."""

    def _get_http_endpoint_from_event(self) -> HttpUrl:
        assert self.__notification_event_handler is not None, "Notification event handler hasn't been set"
        # <###> if you get exception from here, and have consistent way of reproduce please report <###>
        # make sure you didn't forget to call beekeeper.run() method
        addr = self.__notification_event_handler.http_endpoint_from_event
        assert addr is not None, "Endpoint from event was not set"
        return addr

    def export_keys_wallet(
        self, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> list[KeyPair]:
        return self.__exec.export_keys_wallet(
            wallet_name=wallet_name,
            wallet_password=wallet_password,
            extract_to=extract_to,
        )

    @abstractmethod
    def _get_settings(self) -> Settings: ...


class Beekeeper(BeekeeperCommon, SyncRemoteBeekeeper):
    def run(self, *, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        self._clear_session()
        with self.update_settings() as settings:
            self._run(
                settings=cast(Settings, settings),
                additional_cli_arguments=additional_cli_arguments,
            )
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

    def teardown(self) -> None:
        self._close()
        super().teardown()


class AsyncBeekeeper(BeekeeperCommon, AsyncRemoteBeekeeper):
    def run(self, *, additional_cli_arguments: BeekeeperArguments | None = None) -> None:
        self._clear_session()
        with self.update_settings() as settings:
            self._run(
                settings=cast(Settings, settings),
                additional_cli_arguments=additional_cli_arguments,
            )
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

    def teardown(self) -> None:
        self._close()
        super().teardown()
