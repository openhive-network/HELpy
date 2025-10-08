from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [
    "Arguments",
    "ArgumentT",
    "AsyncBeekeeper",
    "AsyncBeekeeperTemplate",
    "AutoCloser",
    "Beekeeper",
    "BeekeeperTemplate",
    "BeekeeperArguments",
    "BeekeeperConfig",
    "BeekeeperExecutable",
    "Config",
    "ConfigT",
    "Executable",
    "match_ports",
    "PortMatchingResult",
    "RunnableHandle",
    "RunnableHandleSettings",
]

if TYPE_CHECKING:
    from beekeepy._executable.abc.arguments import Arguments
    from beekeepy._executable.abc.config import Config
    from beekeepy._executable.abc.executable import ArgumentT, AutoCloser, ConfigT, Executable
    from beekeepy._executable.beekeeper_arguments import BeekeeperArguments
    from beekeepy._executable.beekeeper_config import BeekeeperConfig
    from beekeepy._executable.beekeeper_executable import BeekeeperExecutable
    from beekeepy._runnable_handle._async_additional_definition import AsyncBeekeeper
    from beekeepy._runnable_handle._sync_additional_definition import Beekeeper
    from beekeepy._runnable_handle.match_ports import PortMatchingResult, match_ports
    from beekeepy._runnable_handle.runnable_async_beekeeper import AsyncBeekeeperTemplate
    from beekeepy._runnable_handle.runnable_handle import RunnableHandle
    from beekeepy._runnable_handle.runnable_sync_beekeeper import BeekeeperTemplate
    from beekeepy._runnable_handle.settings import RunnableHandleSettings

__getattr__ = lazy_module_factory(
    globals(),
    # Translations
    *aggregate_same_import(
        "PortMatchingResult",
        "match_ports",
        module="beekeepy._runnable_handle.match_ports",
    ),
    *aggregate_same_import(
        "ArgumentT",
        "AutoCloser",
        "ConfigT",
        "Executable",
        module="beekeepy._executable.abc.executable",
    ),
    ("beekeepy._executable.abc.arguments", "Arguments"),
    ("beekeepy._runnable_handle._async_additional_definition", "AsyncBeekeeper"),
    ("beekeepy._runnable_handle.runnable_async_beekeeper", "AsyncBeekeeperTemplate"),
    ("beekeepy._runnable_handle._sync_additional_definition", "Beekeeper"),
    ("beekeepy._executable.beekeeper_arguments", "BeekeeperArguments"),
    ("beekeepy._executable.beekeeper_config", "BeekeeperConfig"),
    ("beekeepy._executable.beekeeper_executable", "BeekeeperExecutable"),
    ("beekeepy._runnable_handle.runnable_sync_beekeeper", "BeekeeperTemplate"),
    ("beekeepy._executable.abc.config", "Config"),
    ("beekeepy._runnable_handle.runnable_handle", "RunnableHandle"),
    ("beekeepy._runnable_handle.settings", "RunnableHandleSettings"),
)
