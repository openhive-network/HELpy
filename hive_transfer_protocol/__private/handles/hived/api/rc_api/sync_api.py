from __future__ import annotations

from hive_transfer_protocol.__private.handles.abc.api import AbstractSyncApi
from hive_transfer_protocol.__private.interfaces.asset.asset import Hf26Asset  # noqa: TCH001
from schemas import rc_api  # noqa: TCH001


class RcApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def find_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.FindRcAccounts[Hf26Asset.Vests]:
        raise NotImplementedError

    @api
    def get_resource_params(self) -> rc_api.GetResourceParams:
        raise NotImplementedError

    @api
    def get_resource_pool(self) -> rc_api.GetResourcePool:
        raise NotImplementedError

    @api
    def list_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.ListRcAccounts[Hf26Asset.Vests]:
        raise NotImplementedError

    @api
    def list_rc_direct_delegations(self, *, start: tuple[str, str], limit: int) -> rc_api.ListRcDirectDelegations:
        raise NotImplementedError
