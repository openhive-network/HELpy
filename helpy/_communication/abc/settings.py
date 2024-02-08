from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass
class CommunicationSettings:
    max_retries: int = 5
    timeout: timedelta = timedelta(seconds=5)
    period_between_retries: timedelta = timedelta(seconds=1)
