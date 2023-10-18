from __future__ import annotations

from helpy._handles.abc.api import AbstractAsyncApi
from helpy._interfaces.asset.asset import Hf26Asset  # noqa: TCH001
from schemas.apis import rc_api  # noqa: TCH001


class RcApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def find_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.FindRcAccounts[Hf26Asset.VestsT]:
        raise NotImplementedError

    @api
    async def get_resource_params(self) -> rc_api.GetResourceParams:
        raise NotImplementedError

    @api
    async def get_resource_pool(self) -> rc_api.GetResourcePool:
        raise NotImplementedError

    @api
    async def list_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.ListRcAccounts[Hf26Asset.VestsT]:
        raise NotImplementedError

    @api
    async def list_rc_direct_delegations(self, *, start: tuple[str, str], limit: int) -> rc_api.ListRcDirectDelegations:
        raise NotImplementedError
