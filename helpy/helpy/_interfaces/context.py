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
    ) -> bool:
        try:
            if exception is not None:
                return self._handle_exception(exception, traceback)
            self._handle_no_exception()
        finally:
            self._finally()
        return exception is None

    @abstractmethod
    def _enter(self) -> EnterReturnT:
        """Called when __enter__ is called."""

    @abstractmethod
    def _finally(self) -> None:
        """Called _always_ in __exit__ method."""

    def _handle_exception(self, _: BaseException, __: TracebackType | None) -> bool:
        """Called when exception occurred.

        Note:
            * Returning False will reraise error (if occurred)
            * Returning True will suppress all errors
        """
        return False

    def _handle_no_exception(self) -> None:
        """Called when no exception occurred.

        Returns:
            Noting.
        """


class ContextAsync(Generic[EnterReturnT]):
    async def __aenter__(self) -> EnterReturnT:
        return await self._aenter()

    async def __aexit__(
        self, _: type[BaseException] | None, exception: BaseException | None, traceback: TracebackType | None
    ) -> bool:
        try:
            if exception is not None:
                return await self._ahandle_exception(exception, traceback)
            await self._ahandle_no_exception()
        finally:
            await self._afinally()
        return exception is None

    @abstractmethod
    async def _aenter(self) -> EnterReturnT:
        """Called when __enter__ is called."""

    @abstractmethod
    async def _afinally(self) -> None:
        """Called _always_ in __exit__ method."""

    async def _ahandle_exception(self, _: BaseException, __: TracebackType | None) -> bool:
        """Called when exception occurred.

        Note:
            * Returning False will reraise error (if occurred)
            * Returning True will suppress all errors
        """
        return False

    async def _ahandle_no_exception(self) -> None:
        """Called when no exception occurred.

        Returns:
            Noting.
        """
