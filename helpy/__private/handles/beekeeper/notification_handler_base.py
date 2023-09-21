from __future__ import annotations

from typing import TYPE_CHECKING

from helpy.__private.communication.appbase_notification_handler import AppbaseNotificationHandler
from helpy.__private.communication.universal_notification_server import notification
from schemas.notifications import AttemptClosingWallets, OpeningBeekeeperFailed

if TYPE_CHECKING:
    from schemas.notifications import Notification


class BeekeeperNotificationHandler(AppbaseNotificationHandler):
    @notification(AttemptClosingWallets)
    async def _on_attempt_of_closing_wallets(self, notification: Notification[AttemptClosingWallets]) -> None:
        await self.on_attempt_of_closing_wallets(notification)

    @notification(OpeningBeekeeperFailed)
    async def _on_opening_beekeeper_failed(self, notification: Notification[OpeningBeekeeperFailed]) -> None:
        await self.on_opening_beekeeper_failed(notification)

    async def on_attempt_of_closing_wallets(self, notification: Notification[AttemptClosingWallets]) -> None:
        """Called when beekeeper attempts to close wallets in session with given token."""

    async def on_opening_beekeeper_failed(self, notification: Notification[OpeningBeekeeperFailed]) -> None:
        """Called, when beekeeper failed to start, because of already running other beekeeper in selected working directory."""
