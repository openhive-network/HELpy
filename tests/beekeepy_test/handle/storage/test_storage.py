from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest
from local_tools.beekeepy import checkers
from loguru import logger

from beekeepy.exceptions import BeekeeperFailedToStartError, FailedToStartExecutableError
from beekeepy.handle.runnable import Beekeeper
from beekeepy.settings import RunnableHandleSettings

if TYPE_CHECKING:
    from pathlib import Path


def prepare_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir()


def test_multiply_beekeepeer_same_storage(working_directory: Path) -> None:
    """
    Test test_multiply_beekeepeer_same_storage will check, if it is possible to run multiple instances of
    beekeepers pointing to the same storage.
    """
    # ARRANGE
    same_storage = working_directory / "same_storage"
    prepare_directory(same_storage)
    settings = RunnableHandleSettings(working_directory=same_storage)

    # ACT & ASSERT 1
    with Beekeeper(settings=settings, logger=logger) as bk1:
        assert bk1.is_running() is True, "First instance of beekeeper should launch without any problems."

        # ACT & ASSERT 2
        with pytest.raises(BeekeeperFailedToStartError) as exc, Beekeeper(settings=settings, logger=logger):
            pass
        assert isinstance(exc.value.cause, FailedToStartExecutableError)


def test_multiply_beekeepeer_different_storage(working_directory: Path) -> None:
    """
    Test test_multiply_beekeepeer_different_storage will check, if it is possible to run multiple instances of
    beekeepers pointing to the different storage.
    """
    # ARRANGE
    bk1_path = working_directory / "bk1"
    prepare_directory(bk1_path)

    bk2_path = working_directory / "bk2"
    prepare_directory(bk2_path)

    # ACT
    bks: list[Beekeeper] = []
    with Beekeeper(settings=RunnableHandleSettings(working_directory=bk1_path), logger=logger) as bk1, Beekeeper(
        settings=RunnableHandleSettings(working_directory=bk2_path), logger=logger
    ) as bk2:
        # ASSERT
        assert bk1.is_running(), "First instance of beekeeper should be working."
        assert bk2.is_running(), "Second instance of beekeeper should be working."
        bks.extend((bk1, bk2))

    for bk in bks:
        assert (
            checkers.check_for_pattern_in_file(
                bk.settings.ensured_working_directory / "stderr.log",
                "Failed to lock access to wallet directory; is another `beekeeper` running?",
            )
            is False
        ), "There should be an no info about another instance of beekeeper locking wallet directory."


def test_beekeepers_files_generation(beekeeper: Beekeeper) -> None:
    """Test test_beekeepers_files_generation will check if beekeeper files are generated and have same content."""
    # ARRANGE & ACT
    wallet_dir = beekeeper.settings.ensured_working_directory
    beekeeper_wallet_lock_file = wallet_dir / "beekeeper.wallet.lock"

    # ASSERT
    # File beekeeper.wallet.lock holds no value inside, so we need only to check is its exists.
    assert beekeeper_wallet_lock_file.exists() is True, "File 'beekeeper.wallet.lock' should exists"
