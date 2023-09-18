from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from helpy.__private.communication.universal_notification_server import UniversalNotificationServer
from helpy.__private.interfaces.url import HttpUrl
from tests.unit.notification_server_tests.counting_notification_handlers import CountingAppbaseNotificationHandler

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture()
async def counting_appbase_notification_handler() -> CountingAppbaseNotificationHandler:
    return CountingAppbaseNotificationHandler()


@pytest.fixture()
async def counting_appbase_notification_server(
    counting_appbase_notification_handler: CountingAppbaseNotificationHandler,
) -> AsyncIterator[UniversalNotificationServer]:
    server = UniversalNotificationServer(counting_appbase_notification_handler)
    server.run()
    yield server
    await server.close()


@pytest.fixture()
def counting_appbase_notification_server_address(
    counting_appbase_notification_server: UniversalNotificationServer,
) -> HttpUrl:
    return HttpUrl(f"localhost:{counting_appbase_notification_server.port}", protocol="http")
