from __future__ import annotations

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import network_node_api  # noqa: TCH001


class NetworkNodeApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_info(self) -> network_node_api.GetInfo:
        raise NotImplementedError

    @api
    async def add_node(self, *, endpoint: str) -> network_node_api.AddNode:
        raise NotImplementedError

    @api
    async def set_allowed_peers(self, *, allowed_peers: list[str]) -> network_node_api.SetAllowedPeers:
        raise NotImplementedError

    @api
    async def get_connected_peers(self) -> network_node_api.GetConnectedPeers:
        raise NotImplementedError
