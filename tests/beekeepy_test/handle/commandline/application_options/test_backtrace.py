from __future__ import annotations

import time
from typing import TYPE_CHECKING, Literal

import pytest
from local_tools.beekeepy import checkers

from beekeepy.handle.runnable import BeekeeperArguments

if TYPE_CHECKING:
    from beekeepy.handle.runnable import (
        BeekeeperExecutable,
    )


@pytest.mark.parametrize("backtrace", ["yes", "no"])
def test_backtrace(backtrace: Literal["yes", "no"], beekeeper_exe: BeekeeperExecutable) -> None:
    """Test will check command line flag --backtrace."""
    # ARRAGNE & ACT

    with beekeeper_exe.restore_arguments(
        BeekeeperArguments(data_dir=beekeeper_exe.working_directory, backtrace=backtrace)
    ), beekeeper_exe.run(
        blocking=False,
    ):
        time.sleep(0.1)
        # ASSERT
        assert checkers.check_for_pattern_in_file(
            beekeeper_exe.working_directory / "stderr.log",
            "Backtrace on segfault is enabled.",
        ) is (backtrace == "yes")
