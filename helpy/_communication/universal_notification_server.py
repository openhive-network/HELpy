from __future__ import annotations

import asyncio
from collections import defaultdict
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Any, Final

from helpy._communication.abc.notification_handler import NotificationHandler
from helpy._communication.async_server import AsyncHttpServer
from helpy._communication.notification_decorator import _NotificationHandlerWrapper
from helpy._interfaces.context import ContextSync
from helpy.exceptions import HelpyError

if TYPE_CHECKING:
    from helpy import HttpUrl
    from schemas.notifications import KnownNotificationT, Notification


class UnhandledNotificationError(HelpyError):
    def __init__(self, notification: Notification[KnownNotificationT]) -> None:
        super().__init__(
            f"Notification `{notification.name}` does not have any registered method to be passed to.", notification
        )


class UniversalNotificationHandler(NotificationHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__registered_notifications: defaultdict[str, list[_NotificationHandlerWrapper[Any]]] = defaultdict(list)
        super().__init__(*args, **kwargs)

    def setup(self) -> None:
        for member_name in dir(self):
            member_value = getattr(self, member_name)
            if isinstance(member_value, _NotificationHandlerWrapper):
                self.__registered_notifications[member_value.notification_name].append(member_value)

    async def handle_notification(self, notification: Notification[KnownNotificationT]) -> None:
        if (callbacks := self.__registered_notifications.get(notification.name)) is not None:
            for callback in callbacks:
                if callback.notification_condition(notification):
                    await callback.call(self, notification)
                    return

        raise UnhandledNotificationError(notification)


class UniversalNotificationServer(ContextSync[int]):
    def __init__(
        self,
        event_handler: UniversalNotificationHandler,
        notification_endpoint: HttpUrl | None = None,
        *,
        thread_name: str | None = None,
    ) -> None:
        self.__event_handler = event_handler
        self.__event_handler.setup()
        self.__http_server = AsyncHttpServer(self.__event_handler, notification_endpoint=notification_endpoint)
        self.__server_thread: Thread | None = None
        self.__thread_name = thread_name

    def run(self) -> int:
        time_to_launch_notification_server: Final[float] = 0.5
        assert self.__server_thread is None, "Server thread is not None; Is server still running?"

        self.__server_thread = Thread(target=asyncio.run, args=(self.__http_server.run(),), name=self.__thread_name)
        self.__server_thread.start()
        sleep(time_to_launch_notification_server)
        return self.__http_server.port

    def close(self) -> None:
        if self.__server_thread is None:
            return

        self.__http_server.close()
        self.__server_thread.join()
        self.__server_thread = None

    @property
    def port(self) -> int:
        return self.__http_server.port

    def _enter(self) -> int:
        return self.run()

    def _finally(self) -> None:
        self.close()
