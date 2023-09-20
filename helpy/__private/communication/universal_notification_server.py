from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Awaitable, Callable  # noqa: TCH003
from threading import Thread
from time import sleep
from typing import Any, Final, Generic

from pydantic.generics import GenericModel

from helpy.__private.communication.async_server import AsyncHttpServer
from helpy.__private.communication.observer import Observer
from helpy.exceptions import HelpyError
from schemas.jsonrpc import JSONRPCResult, get_response_model
from schemas.notifications import KnownNotificationT, Notification

AnyNotification = Notification[Any]


class UnhandledNotificationError(HelpyError):
    def __init__(self, notification: AnyNotification) -> None:
        super().__init__(
            f"Notification `{notification.name}` does not have any registered method to be passed to.", notification
        )


class NotificationHandler(Observer, ABC):
    async def data_received(self, data: dict[str, Any]) -> None:
        deserialized_notification = get_response_model(Notification[KnownNotificationT], **data)
        assert isinstance(deserialized_notification, JSONRPCResult)
        await self.handle_notification(deserialized_notification.result)

    @abstractmethod
    async def handle_notification(self, notification: Notification[KnownNotificationT]) -> None:
        """Method called after properly serializing notification.

        Args:
            notification (Notification[T]): received notification object
        """


class _NotificationHandlerWrapper(GenericModel, Generic[KnownNotificationT]):
    notification_name: str
    notification_handler: Callable[[Any, Notification[KnownNotificationT]], Awaitable[None]]
    notification_condition: Callable[[Notification[KnownNotificationT]], bool]

    async def call(self, this: Any, notification: Notification[KnownNotificationT]) -> None:
        await self.notification_handler(this, notification)

    async def __call__(self, this: Any, notification: Notification[KnownNotificationT]) -> Any:
        return self.call(this, notification)


def notification(
    type_: type[KnownNotificationT],
    /,
    *,
    condition: Callable[[Notification[KnownNotificationT]], bool] | None = None,
) -> Callable[
    [Callable[[Any, Notification[KnownNotificationT]], Awaitable[None]]],
    _NotificationHandlerWrapper[KnownNotificationT],
]:
    def wrapper(
        callback: Callable[[Any, Notification[KnownNotificationT]], Awaitable[None]]
    ) -> _NotificationHandlerWrapper[KnownNotificationT]:
        result_cls = _NotificationHandlerWrapper[type_]  # type: ignore[valid-type]
        result_cls.update_forward_refs(**locals())
        return result_cls(  # type: ignore[return-value]
            notification_name=type_.get_notification_name(),
            notification_handler=callback,
            notification_condition=condition or (lambda _: True),
        )

    return wrapper


class UniversalNotificationHandler(NotificationHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__registered_notifications: defaultdict[str, list[_NotificationHandlerWrapper[Any]]] = defaultdict(list)

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
