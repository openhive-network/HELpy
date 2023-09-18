from __future__ import annotations

from typing import TYPE_CHECKING

from helpy.__private.communication.universal_notification_server import (
    UniversalNotificationHandler,
    notification,
)
from schemas.notification_model import WebserverListening
from schemas.notification_model.notifications.error_notification import Error
from schemas.notification_model.notifications.status_notification import Status

if TYPE_CHECKING:
    from schemas.notification_model.notification import Notification


class AppbaseNotificationHandler(UniversalNotificationHandler):
    @notification(WebserverListening, condition=lambda n: n.value.type_ == "HTTP")
    async def _on_http_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        await self.on_http_webserver_bind(notification)

    @notification(WebserverListening, condition=lambda n: n.value.type_ == "WS")
    async def _on_ws_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        await self.on_ws_webserver_bind(notification)

    @notification(Status)
    async def _on_status_changed(self, notification: Notification[Status]) -> None:
        await self.on_status_changed(notification)

    @notification(Error)
    async def _on_error(self, notification: Notification[Error]) -> None:
        await self.on_error(notification)

    async def on_http_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        """Called when hived reports http server to be ready."""

    async def on_ws_webserver_bind(self, notification: Notification[WebserverListening]) -> None:
        """Called when hived reports ws server to be ready."""

    async def on_status_changed(self, notification: Notification[Status]) -> None:
        """Called when status of notifier changed."""

    async def on_error(self, notification: Notification[Error]) -> None:
        """Called when notifier reports an error."""
