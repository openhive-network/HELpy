from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import helpy
from helpy._communication.appbase_notification_handler import AppbaseNotificationHandler
from helpy._communication.httpx_communicator import HttpxCommunicator
from schemas.notifications import Notification

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl
    from schemas.notifications import Error, Status, WebserverListening
    from schemas.notifications.abc import NotificationBase


async def send_notification(address: HttpUrl, notification: NotificationBase) -> None:
    communicator = HttpxCommunicator(settings=helpy.Settings())
    await communicator.get_async_client().put(
        address.as_string(),
        headers=communicator._json_headers(),
        content=Notification(name=notification.get_notification_name(), time=datetime.now(), value=notification).json(
            by_alias=True
        ),
    )


class CountingAppbaseNotificationHandler(AppbaseNotificationHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.on_ws_webserver_bind_count: int = 0
        self.on_http_webserver_bind_count: int = 0
        self.on_error_count: int = 0
        self.on_status_changed_count: int = 0

    async def on_ws_webserver_bind(self, _: Notification[WebserverListening]) -> None:
        self.on_ws_webserver_bind_count += 1

    async def on_http_webserver_bind(self, _: Notification[WebserverListening]) -> None:
        self.on_http_webserver_bind_count += 1

    async def on_error(self, _: Notification[Error]) -> None:
        self.on_error_count += 1

    async def on_status_changed(self, _: Notification[Status]) -> None:
        self.on_status_changed_count += 1
