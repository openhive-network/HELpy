from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [
    "AsyncBeekeeper",
    "AsyncSession",
    "AsyncWallet",
    "AsyncUnlockedWallet",
    "close_already_running_beekeeper",
    "find_running_beekeepers",
    "PackedAsyncBeekeeper",
    "InterfaceSettings",
    "Beekeeper",
    "PackedSyncBeekeeper",
    "Session",
    "InterfaceSettings",
    "Wallet",
    "UnlockedWallet",
]

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous import (
        AsyncBeekeeper,
        AsyncSession,
        AsyncUnlockedWallet,
        AsyncWallet,
        PackedAsyncBeekeeper,
    )
    from beekeepy._interface.abc.synchronous import (
        Beekeeper,
        PackedSyncBeekeeper,
        Session,
        UnlockedWallet,
        Wallet,
    )
    from beekeepy._interface.settings import InterfaceSettings
    from beekeepy._runnable_handle.beekeeper_utilities import close_already_running_beekeeper, find_running_beekeepers

__getattr__ = lazy_module_factory(
    globals(),
    # Translations
    *aggregate_same_import(
        "AsyncBeekeeper",
        "PackedAsyncBeekeeper",
        "AsyncSession",
        "AsyncWallet",
        "AsyncUnlockedWallet",
        module="beekeepy._interface.abc.asynchronous",
    ),
    *aggregate_same_import(
        "Beekeeper",
        "PackedSyncBeekeeper",
        "Session",
        "UnlockedWallet",
        "Wallet",
        module="beekeepy._interface.abc.synchronous",
    ),
    ("beekeepy._runnable_handle.beekeeper_utilities", "close_already_running_beekeeper"),
    ("beekeepy._runnable_handle.beekeeper_utilities", "find_running_beekeepers"),
    ("beekeepy._interface.settings", "InterfaceSettings"),
)
