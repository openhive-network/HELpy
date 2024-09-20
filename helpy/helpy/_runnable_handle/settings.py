from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from pydantic import Field

from helpy import Settings as HandleSettings


class Settings(HandleSettings):
    """Defines parameters for beekeeper how to start and behave."""

    working_directory: Path = Field(default_factory=lambda: Path.cwd())
    """Path, where beekeeper binary will store all it's data and logs."""

    binary_path: Path | None = None
    """Alternative path to beekeeper binary."""

    propagate_sigint: bool = True
    """If set to True (default), sigint will be sent to beekeeper without control of this library."""

    close_timeout: timedelta = Field(default_factory=lambda: timedelta(seconds=10.0))
    """This timeout varriable affects time handle waits before beekeepy closes."""
