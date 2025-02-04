from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Final

from helpy import ContextAsync, ContextSync
from helpy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from types import TracebackType


class DelayGuardBase:
    BEEKEEPER_DELAY_TIME: Final[timedelta] = timedelta(seconds=0.6)

    def __init__(self) -> None:
        self._wait_time: Final[float] = 0.1
        self._next_time_unlock: datetime | None = None
        self._exception_occured = False

    def _waiting_should_continue(self) -> bool:
        return self._next_time_unlock is not None and self.__now() < self._next_time_unlock

    def _handle_exception_impl(self, ex: BaseException, _: TracebackType | None) -> bool:
        self._exception_occured = isinstance(ex, ErrorInResponseError)
        self._next_time_unlock = self.__now() + self.BEEKEEPER_DELAY_TIME
        return False

    def _handle_no_exception_impl(self) -> None:
        self._exception_occured = False
        self._next_time_unlock = None

    def error_occured(self) -> bool:
        return self._exception_occured

    def __now(self) -> datetime:
        return datetime.now(timezone.utc)


class SyncDelayGuard(DelayGuardBase, ContextSync["SyncDelayGuard"]):
    def _enter(self) -> SyncDelayGuard:
        while self._waiting_should_continue():
            time.sleep(self._wait_time)
        return self

    def _handle_exception(self, ex: BaseException, tb: TracebackType | None) -> bool:
        return self._handle_exception_impl(ex, tb)

    def _handle_no_exception(self) -> None:
        return self._handle_no_exception_impl()

    def _finally(self) -> None:
        return None


class AsyncDelayGuard(DelayGuardBase, ContextAsync["AsyncDelayGuard"]):
    async def _aenter(self) -> AsyncDelayGuard:
        while self._waiting_should_continue():
            await asyncio.sleep(self._wait_time)
        return self

    async def _ahandle_exception(self, ex: BaseException, tb: TracebackType | None) -> bool:
        return self._handle_exception_impl(ex, tb)

    async def _ahandle_no_exception(self) -> None:
        return self._handle_no_exception_impl()

    async def _afinally(self) -> None:
        return None
