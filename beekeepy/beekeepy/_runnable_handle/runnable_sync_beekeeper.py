from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._remote_handle.sync_beekeeper import Beekeeper as RemoteBeekeeperTemplate
from beekeepy._runnable_handle.runnable_beekeeper import RunnableBeekeeper, RunnableSettingsT

if TYPE_CHECKING:
    from beekeepy._runnable_handle.match_ports import PortMatchingResult
    from beekeepy._runnable_handle.settings import RunnableHandleSettings


class Beekeeper(RunnableBeekeeper, RemoteBeekeeperTemplate[RunnableSettingsT]):
    def _get_settings(self) -> RunnableHandleSettings:
        return self.settings

    def _enter(self) -> Beekeeper[RunnableSettingsT]:
        self.run()
        return self

    def teardown(self) -> None:
        self._close()
        self._clear_session()
        super().teardown()

    def _setup_ports(self, ports: PortMatchingResult) -> None:
        with self.update_settings() as settings:
            self._write_ports(settings, ports)


BeekeeperTemplate = Beekeeper
