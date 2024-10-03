from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Final, TypeVar

from loguru import logger

from beekeepy.exceptions.base import InvalidatedStateError

T = TypeVar("T")

__all__ = ["StateInvalidator"]

EXCLUSIVE_MEMBER_NAME: Final[str] = "_StateInvalidator__invalidated"


def empty_call_after_invalidation(return_after_invalidation: T) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def empty_call_after_invalidation_impl(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func, assigned=("__module__", "__qualname__", "__doc__", "__annotations__"))
        def empty_call_after_invalidation_impl_wrapper(this: StateInvalidator, *args: Any, **kwargs: Any) -> T:
            if isinstance(this, StateInvalidator) and getattr(this, EXCLUSIVE_MEMBER_NAME) is not None:
                logger.warning(f"Ignoring call to {func.__qualname__}")
                return return_after_invalidation
            return func(*[this, *args], **kwargs)

        return empty_call_after_invalidation_impl_wrapper

    return empty_call_after_invalidation_impl


class StateInvalidator:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__invalidated: InvalidatedStateError | None = None
        """This var is set to None if object is valid.

        Note: If it set to exception it is thrown on access to object members after invalidation
        """

        self.__objects_to_invalidate: list[StateInvalidator] = []
        super().__init__(*args, **kwargs)

    @empty_call_after_invalidation(None)
    def invalidate(self, exception: InvalidatedStateError | None = None) -> None:
        exception = exception or InvalidatedStateError()
        for obj in self.__objects_to_invalidate:
            obj.invalidate(exception=exception)
        self.__invalidated = exception

    def register_invalidable(self, obj: StateInvalidator) -> None:
        self.__objects_to_invalidate.append(obj)

    def __getattribute__(self, name: str) -> Any:
        attr_to_return = super().__getattribute__(name)
        invalidated = super().__getattribute__(EXCLUSIVE_MEMBER_NAME)
        if name == EXCLUSIVE_MEMBER_NAME or invalidated is None or StateInvalidator.__is_wrapper(attr_to_return):
            return attr_to_return
        raise self.__invalidated  # type: ignore[misc]

    def __setattr__(self, name: str, value: Any) -> None:
        if name != EXCLUSIVE_MEMBER_NAME and self.__invalidated is not None:
            raise self.__invalidated
        return super().__setattr__(name, value)

    @staticmethod
    def empty_call_after_invalidation(return_after_invalidation: T) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return empty_call_after_invalidation(return_after_invalidation=return_after_invalidation)

    @staticmethod
    def __is_wrapper(obj: Any) -> bool:
        return (
            callable(obj) and hasattr(obj, "__name__") and obj.__name__ == "empty_call_after_invalidation_impl_wrapper"
        )
