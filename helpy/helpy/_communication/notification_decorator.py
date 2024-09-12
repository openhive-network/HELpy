from __future__ import annotations

from collections.abc import Awaitable, Callable  # noqa: TCH003
from typing import Any, Generic

from pydantic.generics import GenericModel

from schemas.notifications import KnownNotificationT, Notification


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
