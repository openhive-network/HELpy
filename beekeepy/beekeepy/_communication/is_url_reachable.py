from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from beekeepy._communication.communicator_getter import get_communicator_cls
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from beekeepy._communication.settings import CommunicationSettings
    from beekeepy._communication.url import HttpUrl

__all__ = [
    "sync_is_url_reachable",
    "async_is_url_reachable",
    "sync_get_first_reachable_url",
    "async_get_first_reachable_url",
]

EXCEPTIONS_TO_CATCH = (CommunicationError, TimeoutError)


def _get_default_settings() -> CommunicationSettings:
    from beekeepy._communication.settings import CommunicationSettings

    return CommunicationSettings(timeout=timedelta(seconds=1))


def sync_is_url_reachable(url: HttpUrl, *, settings: CommunicationSettings | None = None) -> bool:
    """
    Check if the given url is reachable.

    Args:
        url: The URL to check.
    Returns:
        True if the URL is reachable, False otherwise.
    """
    try:
        get_communicator_cls("sync")(settings=(settings or _get_default_settings())).get(url=url)
    except EXCEPTIONS_TO_CATCH:
        return False
    else:
        return True


async def async_is_url_reachable(url: HttpUrl, *, settings: CommunicationSettings | None = None) -> bool:
    """
    Check if the given url is reachable.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is reachable, False otherwise.
    """
    try:
        await get_communicator_cls("async")(settings=(settings or _get_default_settings())).async_get(url=url)
    except EXCEPTIONS_TO_CATCH:
        return False
    else:
        return True


def sync_get_first_reachable_url(
    urls: Sequence[HttpUrl],
    *,
    settings: CommunicationSettings | None = None,
) -> HttpUrl:
    """
    Return the first reachable URL from the list.

    Args:
        urls: Sequence of URLs to check in order.
        settings: Optional communication settings.

    Returns:
        The first URL that is reachable.

    Raises:
        ValueError: If no URL in the list is reachable.
    """
    for url in urls:
        if sync_is_url_reachable(url, settings=settings):
            return url
    raise ValueError(f"No reachable URL found in: {[str(u) for u in urls]}")


async def async_get_first_reachable_url(
    urls: Sequence[HttpUrl],
    *,
    settings: CommunicationSettings | None = None,
) -> HttpUrl:
    """
    Return the first reachable URL from the list.

    Args:
        urls: Sequence of URLs to check in order.
        settings: Optional communication settings.

    Returns:
        The first URL that is reachable.

    Raises:
        ValueError: If no URL in the list is reachable.
    """
    for url in urls:
        if await async_is_url_reachable(url, settings=settings):
            return url
    raise ValueError(f"No reachable URL found in: {[str(u) for u in urls]}")
