from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "AnyUrl",
    "AsyncDelayGuard",
    "ContextAsync",
    "ContextSettingsUpdater",
    "ContextSync",
    "DelayGuardBase",
    "ErrorLogger",
    "HttpUrl",
    "KeyPair",
    "mask",
    "P2PUrl",
    "sanitize",
    "SelfContextAsync",
    "SelfContextSync",
    "SharedSettingsHolder",
    "Stopwatch",
    "StopwatchResult",
    "SuppressApiNotFound",
    "SyncDelayGuard",
    "UniqueSettingsHolder",
    "Url",
    "WsUrl",
]

if TYPE_CHECKING:
    from beekeepy._communication.url import AnyUrl, HttpUrl, P2PUrl, Url, WsUrl
    from beekeepy._utilities.context import ContextAsync, ContextSync, SelfContextAsync, SelfContextSync
    from beekeepy._utilities.context_settings_updater import ContextSettingsUpdater
    from beekeepy._utilities.delay_guard import AsyncDelayGuard, DelayGuardBase, SyncDelayGuard
    from beekeepy._utilities.error_logger import ErrorLogger
    from beekeepy._utilities.key_pair import KeyPair
    from beekeepy._utilities.sanitize import mask, sanitize
    from beekeepy._utilities.settings_holder import SharedSettingsHolder, UniqueSettingsHolder
    from beekeepy._utilities.stopwatch import Stopwatch, StopwatchResult
    from beekeepy._utilities.suppress_api_not_found import SuppressApiNotFound

else:
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        # Translations
        **aggregate_same_import(
            "AnyUrl",
            "HttpUrl",
            "P2PUrl",
            "Url",
            "WsUrl",
            module="beekeepy._communication.url",
        ),
        **aggregate_same_import(
            "ContextAsync",
            "ContextSync",
            "SelfContextAsync",
            "SelfContextSync",
            module="beekeepy._utilities.context",
        ),
        **aggregate_same_import(
            "AsyncDelayGuard",
            "DelayGuardBase",
            "SyncDelayGuard",
            module="beekeepy._utilities.delay_guard",
        ),
        **aggregate_same_import(
            "mask",
            "sanitize",
            module="beekeepy._utilities.sanitize",
        ),
        **aggregate_same_import(
            "SharedSettingsHolder",
            "UniqueSettingsHolder",
            module="beekeepy._utilities.settings_holder",
        ),
        **aggregate_same_import(
            "Stopwatch",
            "StopwatchResult",
            module="beekeepy._utilities.stopwatch",
        ),
        ContextSettingsUpdater="beekeepy._utilities.context_settings_updater",
        ErrorLogger="beekeepy._utilities.error_logger",
        KeyPair="beekeepy._utilities.key_pair",
        SuppressApiNotFound="beekeepy._utilities.suppress_api_not_found",
    )
