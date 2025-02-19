from __future__ import annotations

from contextlib import suppress

from helpy import Beekeeper, HttpUrl, Settings
from helpy.exceptions import CommunicationError, ErrorInResponseError


def close_sessions(http_endpoint: HttpUrl, session_tokens: list[str]) -> None:
    with suppress(CommunicationError), Beekeeper(settings=Settings(http_endpoint=http_endpoint, max_retries=1)) as bk:
        for token in session_tokens:
            with suppress(ErrorInResponseError):
                bk.api.close_session(token=token)
