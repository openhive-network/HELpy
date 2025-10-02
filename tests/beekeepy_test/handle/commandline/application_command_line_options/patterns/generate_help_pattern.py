from __future__ import annotations

from pathlib import Path

import loguru

from beekeepy.handle.runnable import BeekeeperExecutable
from beekeepy.handle.settings import RunnableHandleSettings

if __name__ == "__main__":
    settings = RunnableHandleSettings()
    help_text = BeekeeperExecutable(
        executable_path=settings.binary_path, working_directory=settings.ensured_working_directory, logger=loguru.logger
    ).get_help_text()
    help_pattern_file = Path.cwd() / "help_pattern.txt"
    help_pattern_file.write_text(help_text.strip())
