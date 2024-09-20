from __future__ import annotations

from helpy import HttpUrl  # noqa: TCH001
from helpy._runnable_handle.settings import Settings as RunnableHandleSettings


class Settings(RunnableHandleSettings):
    """Defines parameters for beekeeper how to start and behave."""

    http_endpoint: HttpUrl | None = None  # type: ignore[assignment]
    """Endpoint on which python will communicate with beekeeper, required for remote beekeeper."""

    use_existing_session: str | None = None
    """If set, beekeeper will use given session while connecting to beeekeeper."""
