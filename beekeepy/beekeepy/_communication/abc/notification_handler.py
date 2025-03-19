from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import msgspec

from beekeepy._communication.abc.http_server_observer import HttpServerObserver
from schemas.notifications import KnownNotificationT


class NotificationHandler(HttpServerObserver, ABC):
    async def data_received(self, data: dict[str, Any]) -> None:
        deserialized_notification = msgspec.json.decode(json.dumps(data).encode(), type=KnownNotificationT)
        await self.handle_notification(deserialized_notification)

    @abstractmethod
    async def handle_notification(self, notification: KnownNotificationT) -> None:
        """Method called after properly serializing notification.

        Args:
            notification: received notification object
        """
