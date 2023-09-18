from __future__ import annotations

from typing import TYPE_CHECKING

from helpy.__private.communication.appbase_notification_handler import AppbaseNotificationHandler
from helpy.__private.communication.universal_notification_server import notification
from schemas.notification_model.notifications.p2p_listening import P2PListening
from schemas.notification_model.notifications.switching_forks_notification import SwitchingForks

if TYPE_CHECKING:
    from schemas.notification_model.notification import Notification


class HivedNotificationHandler(AppbaseNotificationHandler):
    @notification(P2PListening)
    async def _on_p2p_server_bind(self, notification: Notification[P2PListening]) -> None:
        await self.on_p2p_server_bind(notification)

    @notification(SwitchingForks)
    async def _on_switching_forks(self, notification: Notification[SwitchingForks]) -> None:
        await self.on_switching_forks(notification)

    async def on_switching_forks(self, notification: Notification[SwitchingForks]) -> None:
        """Called when hived reports p2p server to be ready."""

    async def on_p2p_server_bind(self, notification: Notification[P2PListening]) -> None:
        """Called when hived reports that fork occurred."""
