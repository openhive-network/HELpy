from __future__ import annotations

from threading import Event
from typing import TYPE_CHECKING, Any

from beekeepy._interface.url import HttpUrl
from beekeepy._runnable_handle.notification_handler_base import BeekeeperNotificationHandler
from loguru import logger

if TYPE_CHECKING:
    from beekeepy._runnable_handle.beekeeper_callbacks import BeekeeperNotificationCallbacks
    from schemas.notifications import (
        AttemptClosingWalletsNotification,
        ErrorNotification,
        KnownNotificationT,
        OpeningBeekeeperFailedNotification,
        StatusNotification,
        WebserverListeningNotification,
    )


class NotificationHandler(BeekeeperNotificationHandler):
    def __init__(self, owner: BeekeeperNotificationCallbacks, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__owner = owner

        self.http_listening_event = Event()
        self.http_endpoint_from_event: HttpUrl | None = None

        self.already_working_beekeeper_event = Event()
        self.already_working_beekeeper_http_address: HttpUrl | None = None
        self.already_working_beekeeper_pid: int | None = None

    async def on_attempt_of_closing_wallets(self, notification: AttemptClosingWalletsNotification) -> None:
        self.__owner._handle_wallets_closed(notification.value)

    async def on_opening_beekeeper_failed(self, notification: OpeningBeekeeperFailedNotification) -> None:
        self.already_working_beekeeper_http_address = HttpUrl(
            self.__combine_url_string(
                notification.value.connection.address,
                notification.value.connection.port,
            ),
            protocol="http",
        )
        self.already_working_beekeeper_pid = int(notification.value.pid)
        self.already_working_beekeeper_event.set()
        self.__owner._handle_opening_beekeeper_failed(notification.value)

    async def on_error(self, notification: ErrorNotification) -> None:
        self.__owner._handle_error(notification.value)

    async def on_status_changed(self, notification: StatusNotification) -> None:
        self.__owner._handle_status_change(notification.value)

    async def on_http_webserver_bind(self, notification: WebserverListeningNotification) -> None:
        self.http_endpoint_from_event = HttpUrl(
            self.__combine_url_string(notification.value.address, notification.value.port),
            protocol="http",
        )
        self.http_listening_event.set()
        self.__owner._http_webserver_ready(notification)

    async def handle_notification(self, notification: KnownNotificationT) -> None:
        logger.debug(f"got notification: {notification.json()}")
        return await super().handle_notification(notification)

    def __combine_url_string(self, address: str, port: int) -> str:
        return f"{address}:{port}"
