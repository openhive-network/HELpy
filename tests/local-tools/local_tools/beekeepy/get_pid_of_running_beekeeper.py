from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._handle.beekeeper import AsyncBeekeeper, Beekeeper
from beekeepy._interface.asynchronous.beekeeper import Beekeeper as AsyncBeekeeperImplementation
from beekeepy._interface.synchronous.beekeeper import Beekeeper as SyncBeekeeperImplementation

if TYPE_CHECKING:
    from beekeepy._interface.abc.asynchronous.beekeeper import Beekeeper as AsyncBeekeeperInterface
    from beekeepy._interface.abc.synchronous.beekeeper import Beekeeper as SyncBeekeeperInterface


def get_pid_of_running_beekeeper(beekeeper: AsyncBeekeeperInterface | SyncBeekeeperInterface) -> int:
    assert isinstance(
        beekeeper, AsyncBeekeeperImplementation | SyncBeekeeperImplementation
    ), "Unsupported interface implementation"
    instance = beekeeper._get_instance()
    assert isinstance(instance, AsyncBeekeeper | Beekeeper), "Unsupported handle"
    return instance.pid
