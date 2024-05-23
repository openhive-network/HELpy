from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from helpy._communication.abc.http_server_observer import HttpServerObserver
from schemas.notifications import KnownNotificationT, Notification


class NotificationHandler(HttpServerObserver, ABC):
    async def data_received(self, data: dict[str, Any]) -> None:
        deserialized_notification = Notification(**data)
        await self.handle_notification(deserialized_notification)

    @abstractmethod
    async def handle_notification(self, notification: Notification[KnownNotificationT]) -> None:
        """Method called after properly serializing notification.

        Args:
            notification: received notification object
        """
