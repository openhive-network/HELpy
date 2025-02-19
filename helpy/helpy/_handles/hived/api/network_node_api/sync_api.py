from __future__ import annotations

from beekeepy._remote_handle.abc.api import AbstractSyncApi
from schemas.apis import network_node_api  # noqa: TCH001


class NetworkNodeApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def get_info(self) -> network_node_api.GetInfo:
        raise NotImplementedError

    @api
    def add_node(self, *, endpoint: str) -> network_node_api.AddNode:
        raise NotImplementedError

    @api
    def set_allowed_peers(self, *, allowed_peers: list[str]) -> network_node_api.SetAllowedPeers:
        raise NotImplementedError

    @api
    def get_connected_peers(self) -> network_node_api.GetConnectedPeers:
        raise NotImplementedError
