from __future__ import annotations

from beekeepy._communication.notification_decorator import notification
from beekeepy._communication.universal_notification_server import UniversalNotificationHandler
from schemas.notifications import Error, Status, WebserverListening

from schemas.notifications.notification import (
    ErrorNotification,
    StatusNotification,
    WebserverListeningNotification,
)


class AppbaseNotificationHandler(UniversalNotificationHandler):
    @notification(WebserverListening, condition=lambda n: n.value.type_ == "HTTP")
    async def _on_http_webserver_bind(self, notification: WebserverListeningNotification) -> None:
        await self.on_http_webserver_bind(notification)

    @notification(WebserverListening, condition=lambda n: n.value.type_ == "WS")
    async def _on_ws_webserver_bind(self, notification: WebserverListeningNotification) -> None:
        await self.on_ws_webserver_bind(notification)

    @notification(Status)
    async def _on_status_changed(self, notification: StatusNotification) -> None:
        await self.on_status_changed(notification)

    @notification(Error)
    async def _on_error(self, notification: ErrorNotification) -> None:
        await self.on_error(notification)

    async def on_http_webserver_bind(self, notification: WebserverListeningNotification) -> None:
        """Called when hived reports http server to be ready."""

    async def on_ws_webserver_bind(self, notification: WebserverListeningNotification) -> None:
        """Called when hived reports ws server to be ready."""

    async def on_status_changed(self, notification: StatusNotification) -> None:
        """Called when status of notifier changed."""

    async def on_error(self, notification: ErrorNotification) -> None:
        """Called when notifier reports an error."""
