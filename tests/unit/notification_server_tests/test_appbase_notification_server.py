from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import pytest

from schemas.notification_model.notifications.error_notification import Error
from schemas.notification_model.notifications.listening_notification import WebserverListening
from schemas.notification_model.notifications.status_notification import Status
from tests.unit.notification_server_tests.counting_notification_handlers import (
    CountingAppbaseNotificationHandler,
    send_notification,
)

if TYPE_CHECKING:
    from helpy.__private.interfaces.url import HttpUrl
    from schemas.notification_model.notifications.abc.notification_base import NotificationBase

CounterGetterT = Callable[[CountingAppbaseNotificationHandler], int]
smoke_test_cases: Iterable[tuple[CounterGetterT, NotificationBase]] = (
    (lambda h: h.on_ws_webserver_bind_count, WebserverListening(type_="WS", address="127.0.0.1", port=9090)),
    (lambda h: h.on_http_webserver_bind_count, WebserverListening(type_="HTTP", address="127.0.0.1", port=9090)),
    (lambda h: h.on_error_count, Error(message="some error message")),
    (lambda h: h.on_status_changed_count, Status(current_status="syncing")),
)


@pytest.mark.parametrize(("counter_getter", "notification"), smoke_test_cases)
async def test_smoke(
    counting_appbase_notification_handler: CountingAppbaseNotificationHandler,
    counting_appbase_notification_server_address: HttpUrl,
    counter_getter: CounterGetterT,
    notification: NotificationBase,
) -> None:
    assert counter_getter(counting_appbase_notification_handler) == 0
    await send_notification(counting_appbase_notification_server_address, notification)
    assert counter_getter(counting_appbase_notification_handler) == 1
