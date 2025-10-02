from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._remote_handle.async_beekeeper import AsyncBeekeeper as RemoteBeekeeperTemplate
from beekeepy._runnable_handle.runnable_beekeeper import RunnableBeekeeper, RunnableSettingsT

if TYPE_CHECKING:
    from beekeepy._runnable_handle.match_ports import PortMatchingResult
    from beekeepy._runnable_handle.settings import RunnableHandleSettings


class AsyncBeekeeper(RunnableBeekeeper, RemoteBeekeeperTemplate[RunnableSettingsT]):
    def _get_settings(self) -> RunnableHandleSettings:
        return self.settings

    async def _aenter(self) -> AsyncBeekeeper[RunnableSettingsT]:
        self.run()
        return self

    def teardown(self) -> None:
        self.close()
        self._clear_session()
        super().teardown()

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        with self.update_settings() as settings:
            self._write_ports(settings, ports)


AsyncBeekeeperTemplate = AsyncBeekeeper
