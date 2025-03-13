from __future__ import annotations

from collections.abc import Awaitable, Callable  # noqa: TCH003
from typing import Any, Generic, TypeVar

from schemas.notifications import NotificationBase

NotificationT = TypeVar("NotificationT", bound=NotificationBase)


class _NotificationHandlerWrapper(Generic[NotificationT]):
    def __init__(
        self,
        notification_name: str,
        notification_handler: Callable[[Any, NotificationT], Awaitable[None]],
        notification_condition: Callable[[NotificationT], bool],
    ) -> None:
        self.notification_name = notification_name
        self.notification_handler = notification_handler
        self.notification_condition = notification_condition

    async def call(self, this: Any, notification: NotificationT) -> None:
        await self.notification_handler(this, notification)

    async def __call__(self, this: Any, notification: NotificationT) -> Any:
        return self.call(this, notification)


def notification(
    type_: type[NotificationT],
    /,
    *,
    condition: Callable[[NotificationT], bool] | None = None,
) -> Callable[[Callable[[Any, NotificationT], Awaitable[None]]], _NotificationHandlerWrapper[NotificationT]]:
    def wrapper(
        callback: Callable[[Any, NotificationT], Awaitable[None]],
    ) -> _NotificationHandlerWrapper[NotificationT]:
        result_cls = _NotificationHandlerWrapper
        return result_cls(
            notification_name=type_.get_notification_name(),
            notification_handler=callback,
            notification_condition=condition or (lambda _: True),
        )

    return wrapper
