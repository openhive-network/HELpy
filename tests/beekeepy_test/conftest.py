from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Iterator

import pytest
from loguru import logger

from beekeepy.handle.settings import InterfaceSettings

if TYPE_CHECKING:
    from pathlib import Path

    from local_tools.beekeepy.models import SettingsFactory, SettingsLoggerFactory
    from loguru import Logger


@pytest.fixture
def settings(working_directory: Path) -> SettingsFactory:
    @wraps(settings)
    def _factory(settings_update: InterfaceSettings | None = None) -> InterfaceSettings:
        amount_of_beekeepers_in_working_directory = len([x for x in working_directory.glob("Beekeeper*") if x.is_dir()])
        working_dir = working_directory / f"Beekeeper{amount_of_beekeepers_in_working_directory}"
        result = settings_update or InterfaceSettings()
        result.working_directory = working_dir
        return result

    return _factory


@pytest.fixture
def settings_with_logger(request: pytest.FixtureRequest, settings: SettingsFactory) -> Iterator[SettingsLoggerFactory]:
    handlers_to_remove: list[int] = []

    @wraps(settings_with_logger)
    def _factory(settings_update: InterfaceSettings | None = None) -> tuple[InterfaceSettings, Logger]:
        sets = settings(settings_update)
        test_name = request.node.name
        log = logger.bind(test_name=test_name)
        handlers_to_remove.append(
            log.add(
                sets.ensured_working_directory / "beekeeper.log",
                filter=lambda params: params["extra"].get("test_name") == test_name,
            )
        )
        return sets, log

    yield _factory

    for hid in handlers_to_remove:
        logger.remove(hid)
