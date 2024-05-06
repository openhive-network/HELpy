from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from helpy._handles.abc.api import AbstractAsyncApi, ApiArgumentSerialization
from helpy._handles.hived.api.wallet_bridge_api.common import WalletBridgeApiCommons
from helpy._interfaces.asset.asset import Hf26Asset  # noqa: TCH001
from schemas.apis import wallet_bridge_api  # noqa: TCH001
from schemas.transaction import Transaction  # noqa: TCH001


class WalletBridgeApi(AbstractAsyncApi, WalletBridgeApiCommons):
    api = AbstractAsyncApi._endpoint

    def argument_serialization(self) -> ApiArgumentSerialization:
        return ApiArgumentSerialization.DOUBLE_ARRAY

    @api
    async def get_version(self) -> wallet_bridge_api.GetVersion:
        raise NotImplementedError

    @api
    async def get_block(self, block: int, /) -> wallet_bridge_api.GetBlock:
        raise NotImplementedError

    @api
    async def get_chain_properties(self) -> wallet_bridge_api.GetChainProperties[Hf26Asset.HiveT]:
        raise NotImplementedError

    @api
    async def get_witness_schedule(self) -> wallet_bridge_api.GetWitnessSchedule:
        raise NotImplementedError

    @api
    async def get_current_median_history_price(self) -> wallet_bridge_api.GetCurrentMedianHistoryPrice:
        raise NotImplementedError

    @api
    async def get_hardfork_version(self) -> wallet_bridge_api.GetHardforkVersion:
        raise NotImplementedError

    @api
    async def get_ops_in_block(self, block: int, only_virtual: bool = False, /) -> wallet_bridge_api.GetOpsInBlock:
        raise NotImplementedError

    @api
    async def get_feed_history(self) -> wallet_bridge_api.GetFeedHistory:
        raise NotImplementedError

    @api
    async def get_active_witnesses(self, include_future: bool, /) -> wallet_bridge_api.GetActiveWitnesses:
        raise NotImplementedError

    @api
    async def get_withdraw_routes(
        self, account: str, destination: WalletBridgeApi.WITHDRAW_ROUTE_TYPES, /
    ) -> wallet_bridge_api.GetWithdrawRoutes:
        raise NotImplementedError

    @api
    async def list_my_accounts(self, accounts: list[str], /) -> wallet_bridge_api.ListMyAccounts:
        raise NotImplementedError

    @api
    async def list_accounts(self, start: str, limit: int, /) -> wallet_bridge_api.ListAccounts:
        raise NotImplementedError

    @api
    async def get_dynamic_global_properties(self) -> wallet_bridge_api.GetDynamicGlobalProperties:
        raise NotImplementedError

    @api
    async def get_account(self, account: str, /) -> wallet_bridge_api.GetAccount:
        raise NotImplementedError

    @api
    async def get_accounts(self, accounts: list[str], /) -> wallet_bridge_api.GetAccounts:
        raise NotImplementedError

    @api
    async def get_transaction(self, transaction_id: str, /) -> wallet_bridge_api.GetTransaction:
        raise NotImplementedError

    @api
    async def list_witnesses(self, start: str, limit: int, /) -> wallet_bridge_api.ListWitnesses:
        raise NotImplementedError

    @api
    async def get_witness(self, witness: str, /) -> wallet_bridge_api.GetWitness:
        raise NotImplementedError

    @api
    async def get_conversion_requests(self, account: str, /) -> wallet_bridge_api.GetConversionRequests:
        raise NotImplementedError

    @api
    async def get_collateralized_conversion_requests(
        self, account: str, /
    ) -> wallet_bridge_api.GetCollateralizedConversionRequests:
        raise NotImplementedError

    @api
    async def get_order_book(self, limit: int, /) -> wallet_bridge_api.GetOrderBook:
        raise NotImplementedError

    @api
    async def get_open_orders(self, account: str, /) -> wallet_bridge_api.GetOpenOrders:
        raise NotImplementedError

    @api
    async def get_owner_history(self, account: str, /) -> wallet_bridge_api.GetOwnerHistory:
        raise NotImplementedError

    @api
    async def get_account_history(self, account: str, start: int, limit: int, /) -> wallet_bridge_api.GetAccountHistory:
        raise NotImplementedError

    @api
    async def list_proposals(
        self,
        start: datetime,
        limit: int,
        order: WalletBridgeApi.SORT_TYPES,
        direction: WalletBridgeApi.SORT_DIRECTION,
        status: WalletBridgeApi.PROPOSAL_STATUS,
    ) -> wallet_bridge_api.ListProposals:
        raise NotImplementedError

    @api
    async def find_proposals(self, proposal_ids: list[int], /) -> wallet_bridge_api.FindProposals:
        raise NotImplementedError

    @api
    async def is_known_transaction(self, transaction_id: str, /) -> wallet_bridge_api.IsKnownTransaction:
        raise NotImplementedError

    @api
    async def list_proposal_votes(
        self,
        start: datetime,
        limit: int,
        order: WalletBridgeApi.SORT_TYPES,
        direction: WalletBridgeApi.SORT_DIRECTION,
        status: WalletBridgeApi.PROPOSAL_STATUS,
    ) -> wallet_bridge_api.ListProposalVotes:
        raise NotImplementedError

    @api
    async def get_reward_fund(self, reward_fund_account: str, /) -> wallet_bridge_api.GetRewardFund:
        raise NotImplementedError

    @api
    async def broadcast_transaction_synchronous(
        self, transaction: Transaction, /
    ) -> wallet_bridge_api.BroadcastTransactionSynchronous:
        raise NotImplementedError

    @api
    async def broadcast_transaction(self, transaction: Transaction, /) -> wallet_bridge_api.BroadcastTransaction:
        raise NotImplementedError

    @api
    async def find_recurrent_transfers(self, account: str, /) -> wallet_bridge_api.FindRecurrentTransfers:
        raise NotImplementedError

    @api
    async def find_rc_accounts(self, accounts: list[str], /) -> wallet_bridge_api.FindRcAccounts:
        raise NotImplementedError

    @api
    async def list_rc_accounts(self, start: str, limit: int, /) -> wallet_bridge_api.ListRcAccounts:
        raise NotImplementedError

    @api
    async def list_rc_direct_delegations(
        self, start: datetime, limit: int, /
    ) -> wallet_bridge_api.ListRcDirectDelegations:
        raise NotImplementedError
