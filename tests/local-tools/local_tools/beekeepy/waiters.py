from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from local_tools.beekeepy import checkers

if TYPE_CHECKING:
    from beekeepy._handle import Beekeeper


def wait_for_beekeeper_to_close(beekeeper: Beekeeper, timeout_seconds: int = 10) -> None:
    start = datetime.now(timezone.utc)
    while (datetime.now(timezone.utc) - start).total_seconds() <= timeout_seconds:
        if checkers.check_for_pattern_in_file(beekeeper.settings.working_directory / "stderr.log", "exited cleanly"):
            return
    raise TimeoutError
