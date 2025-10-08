from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [
    "AsyncBeekeepyService",
    "create_async_beekeeper_service",
    "BeekeepyService",
    "create_beekeepy_service",
]


if TYPE_CHECKING:
    from beekeepy._service.asynchronous import AsyncBeekeepyService, create_async_beekeeper_service
    from beekeepy._service.synchronous import BeekeepyService, create_beekeepy_service

__getattr__ = lazy_module_factory(
    globals(),
    # Translations
    *aggregate_same_import(
        "create_async_beekeeper_service",
        "AsyncBeekeepyService",
        module="beekeepy._service.asynchronous",
    ),
    *aggregate_same_import(
        "create_beekeeper_service",
        "BeekeepyService",
        module="beekeepy._service.synchronous",
    ),
)
