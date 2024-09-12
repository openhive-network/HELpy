from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

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
        self.__result = StopwatchResult(started_at=datetime.now(), stopped_at=datetime.now())
        super().__init__(*args, **kwargs)

    def _enter(self) -> StopwatchResult:
        return self.__result

    def _finally(self) -> None:
        self.__result.stopped_at = datetime.now()
