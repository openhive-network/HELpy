from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Any, Final

from helpy.__private.communication.async_server import AsyncHttpServer, Observer
from helpy.exceptions import HelpyError
from schemas.__private.hive_factory import HiveError, HiveResult
from schemas.notification_model.notification import Notification

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from schemas.notification_model.notifications import SupportedNotificationT

AnyNotification = Notification[Any]


class UnhandledNotificationError(HelpyError):
    def __init__(self, notification: AnyNotification) -> None:
        super().__init__(
            f"Notification `{notification.name}` does not have any registered method to be passed to.", notification
        )


class NotificationHandler(Observer, ABC):
    async def data_received(self, data: dict[str, Any]) -> None:
        deserialized_notification: HiveResult[AnyNotification] | HiveError = HiveResult.factory(Notification, **data)
        assert isinstance(deserialized_notification, HiveResult)
        await self.handle_notification(deserialized_notification.result)

    @abstractmethod
    async def handle_notification(self, notification: Notification[SupportedNotificationT]) -> None:
        """Method called after properly serializing notification.

        Args:
            notification (Notification[T]): received notification object
        """


@dataclass
class _NotificationHandlerWrapper:
    notification_name: str
    notification_handler: Callable[[Any, Notification[SupportedNotificationT]], Awaitable[None]]
    notification_condition: Callable[[Notification[SupportedNotificationT]], bool]

    async def call(self, this: Any, notification: Notification[SupportedNotificationT]) -> None:
        await self.notification_handler(this, notification)


def notification(
    type_: type[SupportedNotificationT],
    /,
    *,
    condition: Callable[[Notification[SupportedNotificationT]], bool] | None = None,
) -> Callable[[Callable[[Any, Notification[SupportedNotificationT]], Awaitable[None]]], _NotificationHandlerWrapper]:
    def wrapper(
        callback: Callable[[Any, Notification[SupportedNotificationT]], Awaitable[None]]
    ) -> _NotificationHandlerWrapper:
        return _NotificationHandlerWrapper(
            notification_name=type_.get_notification_name(),
            notification_handler=callback,
            notification_condition=condition or (lambda _: True),
        )

    return wrapper


class UniversalNotificationHandler(NotificationHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__registered_notifications: defaultdict[str, list[_NotificationHandlerWrapper]] = defaultdict(list)

    def setup(self) -> None:
        for member_name in dir(self):
            member_value = getattr(self, member_name)
            if isinstance(member_value, _NotificationHandlerWrapper):
                self.__registered_notifications[member_value.notification_name].append(member_value)

    async def handle_notification(self, notification: Notification[SupportedNotificationT]) -> None:
        if (callbacks := self.__registered_notifications.get(notification.name)) is not None:
            for callback in callbacks:
                if callback.notification_condition(notification):
                    await callback.call(self, notification)
                    return

        raise UnhandledNotificationError(notification)


class UniversalNotificationServer:
    def __init__(self, event_handler: UniversalNotificationHandler) -> None:
        self.__event_handler = event_handler
        self.__event_handler.setup()
        self.__http_server = AsyncHttpServer(self.__event_handler)
        self.__server_thread: Thread | None = None

    def run(self) -> int:
        time_to_launch_notification_server: Final[float] = 0.5
        assert self.__server_thread is None

        self.__server_thread = Thread(target=asyncio.run, args=(self.__http_server.run(),))
        self.__server_thread.start()
        sleep(time_to_launch_notification_server)
        return self.__http_server.port

    def close(self) -> None:
        assert self.__server_thread is not None

        self.__http_server.close()
        self.__server_thread.join()
        self.__server_thread = None

    @property
    def port(self) -> int:
        return self.__http_server.port
