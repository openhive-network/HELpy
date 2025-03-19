from __future__ import annotations

from beekeepy._communication.appbase_notification_handler import AppbaseNotificationHandler
from beekeepy._communication.notification_decorator import notification
from schemas.notifications import (
    AttemptClosingWalletsNotification,
    OpeningBeekeeperFailedNotification,
)


class BeekeeperNotificationHandler(AppbaseNotificationHandler):
    @notification(AttemptClosingWalletsNotification)
    async def _on_attempt_of_closing_wallets(self, notification: AttemptClosingWalletsNotification) -> None:
        await self.on_attempt_of_closing_wallets(notification)

    @notification(OpeningBeekeeperFailedNotification)
    async def _on_opening_beekeeper_failed(self, notification: OpeningBeekeeperFailedNotification) -> None:
        await self.on_opening_beekeeper_failed(notification)

    async def on_attempt_of_closing_wallets(self, notification: AttemptClosingWalletsNotification) -> None:
        """Called when beekeeper attempts to close wallets in session with given token."""

    async def on_opening_beekeeper_failed(self, notification: OpeningBeekeeperFailedNotification) -> None:
        """Called, when beekeeper failed to start.

        That is because of already running other beekeeper in selected working directory.
        """
