from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.handle.runnable import BeekeeperExecutable

if TYPE_CHECKING:
    from local_tools.beekeepy.models import SettingsLoggerFactory


@pytest.fixture
def beekeeper_exe(settings_with_logger: SettingsLoggerFactory) -> BeekeeperExecutable:
    incoming_settings, logger = settings_with_logger()
    return BeekeeperExecutable(
        executable_path=incoming_settings.binary_path,
        working_directory=incoming_settings.ensured_working_directory,
        logger=logger,
    )
