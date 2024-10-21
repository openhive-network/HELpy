from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from local_tools.beekeepy import checkers

from beekeepy._executable.beekeeper_arguments import BeekeeperArguments

if TYPE_CHECKING:
    from beekeepy._handle.beekeeper import Beekeeper


@pytest.mark.parametrize("webserver_thread_pool_size", [1, 2, 4, 8])
def test_webserver_thread_pool_size(beekeeper_not_started: Beekeeper, webserver_thread_pool_size: int) -> None:
    """Test will check command line flag --webserver-thread-pool-size."""
    # ARRANGE & ACT
    beekeeper_not_started.run(
        additional_cli_arguments=BeekeeperArguments(webserver_thread_pool_size=webserver_thread_pool_size)
    )

    # ASSERT
    assert checkers.check_for_pattern_in_file(
        beekeeper_not_started.settings.working_directory / "stderr.log",
        f"configured with {webserver_thread_pool_size} thread pool size",
    )
