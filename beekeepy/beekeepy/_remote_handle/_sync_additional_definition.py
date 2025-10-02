from __future__ import annotations

from beekeepy._remote_handle.settings import RemoteHandleSettings
from beekeepy._remote_handle.sync_beekeeper import SyncBeekeeperTemplate

Beekeeper = SyncBeekeeperTemplate[RemoteHandleSettings]
