from __future__ import annotations

from typing import TYPE_CHECKING

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
else:
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        # Translations
        **aggregate_same_import(
            "PortMatchingResult",
            "match_ports",
            module="beekeepy._runnable_handle.match_ports",
        ),
        **aggregate_same_import(
            "ArgumentT",
            "AutoCloser",
            "ConfigT",
            "Executable",
            module="beekeepy._executable.abc.executable",
        ),
        Arguments="beekeepy._executable.abc.arguments",
        AsyncBeekeeper="beekeepy._runnable_handle._async_additional_definition",
        AsyncBeekeeperTemplate="beekeepy._runnable_handle.runnable_async_beekeeper",
        Beekeeper="beekeepy._runnable_handle._sync_additional_definition",
        BeekeeperArguments="beekeepy._executable.beekeeper_arguments",
        BeekeeperConfig="beekeepy._executable.beekeeper_config",
        BeekeeperExecutable="beekeepy._executable.beekeeper_executable",
        BeekeeperTemplate="beekeepy._runnable_handle.runnable_sync_beekeeper",
        Config="beekeepy._executable.abc.config",
        RunnableHandle="beekeepy._runnable_handle.runnable_handle",
        RunnableHandleSettings="beekeepy._runnable_handle.settings",
    )
