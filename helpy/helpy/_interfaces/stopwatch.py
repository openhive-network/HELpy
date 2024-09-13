from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from pytz import utc

from helpy._interfaces.context import ContextSync


@dataclass
class StopwatchResult:
    started_at: datetime
    stopped_at: datetime

    @property
    def seconds_delta(self) -> float:
        return self.delta.total_seconds()

    @property
    def delta(self) -> timedelta:
        return self.stopped_at - self.started_at


class Stopwatch(ContextSync[StopwatchResult]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__result = StopwatchResult(started_at=self.__now(), stopped_at=self.__now())
        super().__init__(*args, **kwargs)

    def _enter(self) -> StopwatchResult:
        return self.__result

    def _finally(self) -> None:
        self.__result.stopped_at = self.__now()

    def __now(self) -> datetime:
        return datetime.now(tz=utc)
