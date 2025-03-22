from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from beekeepy._utilities.context import ContextSync


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

    @property
    def lap(self) -> float:
        return (Stopwatch.now() - self.started_at).total_seconds()


class Stopwatch(ContextSync[StopwatchResult]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__result = StopwatchResult(started_at=self.now(), stopped_at=self.now())
        super().__init__(*args, **kwargs)

    def _enter(self) -> StopwatchResult:
        return self.__result

    def _finally(self) -> None:
        self.__result.stopped_at = self.now()

    @classmethod
    def now(cls) -> datetime:
        return datetime.now(tz=timezone.utc)
