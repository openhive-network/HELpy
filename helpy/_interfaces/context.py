from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from types import TracebackType

EnterReturnT = TypeVar("EnterReturnT")


class ContextSync(Generic[EnterReturnT]):
    def __enter__(self) -> EnterReturnT:
        return self._enter()

    def __exit__(
        self, _: type[BaseException] | None, exception: BaseException | None, traceback: TracebackType | None
    ) -> bool | None:
        try:
            if exception is not None:
                return self._handle_exception(exception, traceback)
        finally:
            self._finally()
        return None

    @abstractmethod
    def _enter(self) -> EnterReturnT:
        """Called when __enter__ is called."""

    @abstractmethod
    def _finally(self) -> None:
        """Called _always_ in __exit__ method."""

    def _handle_exception(self, exception: BaseException, traceback: TracebackType | None) -> bool | None:
        """Called when exception occurred."""


class ContextAsync(Generic[EnterReturnT]):
    async def __aenter__(self) -> EnterReturnT:
        return await self._enter()

    async def __aexit__(
        self, _: type[BaseException] | None, exception: BaseException | None, traceback: TracebackType | None
    ) -> bool | None:
        try:
            if exception is not None:
                return await self._handle_exception(exception, traceback)
        finally:
            await self._finally()
        return None

    @abstractmethod
    async def _enter(self) -> EnterReturnT:
        """Called when __enter__ is called."""

    @abstractmethod
    async def _finally(self) -> None:
        """Called _always_ in __exit__ method."""

    async def _handle_exception(self, exception: BaseException, traceback: TracebackType | None) -> bool | None:
        """Called when exception occurred."""
