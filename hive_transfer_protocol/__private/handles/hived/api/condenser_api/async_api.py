from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi
from hive_transfer_protocol.__private.handles.hived.api.condenser_api.common import CondenserApiCommons
from schemas.condenser_api import response_schemas as condenser_api  # noqa: TCH001
from schemas.transaction_model.transaction import LegacyTransaction  # noqa: TCH001

if TYPE_CHECKING:
    from datetime import datetime


class CondenserApi(AbstractAsyncApi, CondenserApiCommons):
    api = AbstractAsyncApi._endpoint

    @classmethod
    def _serialize_params(cls, args: Any, kwargs: dict[str, Any]) -> str:  # noqa: ARG003
        return cls._legacy_serialization(args=args)

    @api
    async def get_version(self) -> condenser_api.GetVersion:
        raise NotImplementedError

    @api
    async def get_active_witnesses(self, /, include_future: bool = False) -> condenser_api.GetActiveWitnesses:
        raise NotImplementedError

    @api
    async def get_block_header(self, /, block_num: int) -> condenser_api.GetBlockHeader:
        raise NotImplementedError

    @api
    async def get_block(self, /, block_num: int) -> condenser_api.GetBlock:
        raise NotImplementedError

    @api
    async def get_ops_in_block(self, /, block_num: int, only_virtual: bool = False) -> condenser_api.GetOpsInBlock:
        raise NotImplementedError

    @api
    async def get_config(self) -> condenser_api.GetConfig:
        raise NotImplementedError

    @api
    async def get_dynamic_global_properties(self) -> condenser_api.GetDynamicGlobalProperties:
        raise NotImplementedError

    @api
    async def get_chain_properties(self) -> condenser_api.GetChainProperties:
        raise NotImplementedError

    @api
    async def get_current_median_history_price(self) -> condenser_api.GetCurrentMedianHistoryPrice:
        raise NotImplementedError

    @api
    async def get_feed_history(self) -> condenser_api.GetFeedHistory:
        raise NotImplementedError

    @api
    async def get_witness_schedule(self, /, include_future: bool = False) -> condenser_api.GetWitnessSchedule:
        raise NotImplementedError

    @api
    async def get_hardfork_version(self) -> condenser_api.GetHardforkVersion:
        raise NotImplementedError

    @api
    async def get_next_scheduled_hardfork(self) -> condenser_api.GetNextScheduledHardfork:
        raise NotImplementedError

    @api
    async def get_reward_fund(self, /, name: str) -> condenser_api.GetRewardFund:
        raise NotImplementedError

    @api
    async def get_key_references(self, /, key: str) -> condenser_api.GetKeyReferences:
        raise NotImplementedError

    @api
    async def get_accounts(
        self, /, accounts: list[str], delayed_votes_active: bool = True
    ) -> condenser_api.GetAccounts:
        raise NotImplementedError

    @api
    async def lookup_account_names(
        self, /, accounts: list[str], delayed_votes_active: bool = True
    ) -> condenser_api.LookupAccountNames:
        raise NotImplementedError

    @api
    async def lookup_accounts(self, /, lower_bound_name: str, limit: int) -> condenser_api.LookupAccounts:
        raise NotImplementedError

    @api
    async def get_account_count(self) -> condenser_api.GetAccountCount:
        raise NotImplementedError

    @api
    async def get_owner_history(self, /, owner: str) -> condenser_api.GetOwnerHistory:
        raise NotImplementedError

    @api
    async def get_recovery_request(self, /, account: str) -> condenser_api.GetRecoveryRequest:
        raise NotImplementedError

    @api
    async def get_escrow(
        self, /, start: tuple[str, int] | tuple[bool, datetime, int], limit: int, order: CondenserApi.SORT_TYPES
    ) -> condenser_api.GetEscrow:
        raise NotImplementedError

    @api
    async def get_withdraw_routes(
        self, /, account: str, destination: CondenserApi.WITHDRAW_ROUTE_TYPES
    ) -> condenser_api.GetWithdrawRoutes:
        raise NotImplementedError

    @api
    async def get_savings_withdraw_from(self, /, account: str) -> condenser_api.GetSavingsWithdrawFrom:
        raise NotImplementedError

    @api
    async def get_savings_withdraw_to(self, /, account: str) -> condenser_api.GetSavingsWithdrawTo:
        raise NotImplementedError

    @api
    async def get_vesting_delegations(
        self, /, account: str, start: str, limit: int = 100
    ) -> condenser_api.GetVestingDelegations:
        raise NotImplementedError

    @api
    async def get_expiring_vesting_delegations(
        self, /, account: str, start: str, limit: int = 100
    ) -> condenser_api.GetExpiringVestingDelegations:
        raise NotImplementedError

    @api
    async def get_witnesses(self, /, witness_ids: list[int]) -> condenser_api.GetWitnesses:
        raise NotImplementedError

    @api
    async def get_conversion_requests(self, /, account: str) -> condenser_api.GetConversionRequests:
        raise NotImplementedError

    @api
    async def get_collateralized_conversion_requests(
        self, /, account: str
    ) -> condenser_api.GetCollateralizedConversionRequests:
        raise NotImplementedError

    @api
    async def get_witness_by_account(self, /, account: str) -> condenser_api.GetWitnessByAccount:
        raise NotImplementedError

    @api
    async def get_witnesses_by_vote(self, /, start_name: str, limit: int) -> condenser_api.GetWitnessesByVote:
        raise NotImplementedError

    @api
    async def lookup_witness_accounts(self, /, start: str, limit: int) -> condenser_api.LookupWitnessAccounts:
        raise NotImplementedError

    @api
    async def get_witness_count(self) -> condenser_api.GetWitnessCount:
        raise NotImplementedError

    @api
    async def get_open_orders(self, /, owner: str) -> condenser_api.GetOpenOrders:
        raise NotImplementedError

    @api
    async def get_transaction_hex(self, /, transaction: LegacyTransaction) -> condenser_api.GetTransactionHex:
        raise NotImplementedError

    @api
    async def get_transaction(self, /, transaction_id: str) -> condenser_api.GetTransaction:
        raise NotImplementedError

    @api
    async def get_required_signatures(
        self, /, transaction: LegacyTransaction, public_key: str
    ) -> condenser_api.GetRequiredSignatures:
        raise NotImplementedError

    @api
    async def get_potential_signatures(self, /, transaction: LegacyTransaction) -> condenser_api.GetPotentialSignatures:
        raise NotImplementedError

    @api
    async def verify_authority(self, /, transaction: LegacyTransaction) -> condenser_api.VerifyAuthority:
        raise NotImplementedError

    @api
    async def verify_account_authority(self, /, transaction: LegacyTransaction) -> condenser_api.VerifyAccountAuthority:
        raise NotImplementedError

    @api
    async def get_active_votes(self, /, author: str, permlink: str) -> condenser_api.GetActiveVotes:
        raise NotImplementedError

    @api
    async def get_account_history(
        self,
        account: str,
        start: int,
        limit: int,
        operation_filter_low: int | None = None,
        operation_filter_high: int | None = None,
    ) -> condenser_api.GetAccountHistory:
        raise NotImplementedError

    @api
    async def broadcast_transaction(self, /, transaction: LegacyTransaction) -> condenser_api.BroadcastTransaction:
        raise NotImplementedError

    @api
    async def broadcast_transaction_synchronous(
        self, /, transaction: LegacyTransaction
    ) -> condenser_api.BroadcastTransactionSynchronous:
        raise NotImplementedError

    @api
    async def get_account_reputations(self, /, account: str, limit: int = 1000) -> condenser_api.GetAccountReputations:
        raise NotImplementedError

    @api
    async def get_ticker(self) -> condenser_api.GetTicker:
        raise NotImplementedError

    @api
    async def get_volume(self) -> condenser_api.GetVolume:
        raise NotImplementedError

    @api
    async def get_order_book(self, /, limit: int = 500) -> condenser_api.GetOrderBook:
        raise NotImplementedError

    @api
    async def get_trade_history(
        self, /, start: datetime, stop: datetime, limit: int = 1000
    ) -> condenser_api.GetTradeHistory:
        raise NotImplementedError

    @api
    async def get_recent_trades(self, /, limit: int = 1000) -> condenser_api.GetRecentTrades:
        raise NotImplementedError

    @api
    async def get_market_history(
        self, /, bucket_seconds: int, start: datetime, stop: datetime
    ) -> condenser_api.GetMarketHistory:
        raise NotImplementedError

    @api
    async def get_market_history_buckets(self) -> condenser_api.GetMarketHistoryBuckets:
        raise NotImplementedError

    @api
    async def is_known_transaction(self, /, transaction_id: str) -> condenser_api.IsKnownTransaction:
        raise NotImplementedError

    @api
    async def list_proposals(
        self,
        start: list[str] | list[int] | list[datetime],
        limit: int,
        order: CondenserApi.SORT_TYPES,
        direction: CondenserApi.SORT_DIRECTION = "ascending",
        status: CondenserApi.PROPOSAL_STATUS = "all",
        last_id: int | None = None,
    ) -> condenser_api.ListProposals:
        raise NotImplementedError

    @api
    async def find_proposals(self, /, proposals_ids: list[int]) -> condenser_api.FindProposals:
        raise NotImplementedError

    @api
    async def list_proposal_votes(
        self,
        start: list[str],
        limit: int,
        order: CondenserApi.SORT_TYPES,
        order_direction: CondenserApi.SORT_DIRECTION,
        status: CondenserApi.PROPOSAL_STATUS,
    ) -> condenser_api.ListProposalVotes:
        raise NotImplementedError

    @api
    async def find_recurrent_transfers(self, /, account: str) -> condenser_api.FindRecurrentTransfers:
        raise NotImplementedError

    @api
    async def find_rc_accounts(self, /, accounts: list[str]) -> condenser_api.FindRcAccounts:
        raise NotImplementedError

    @api
    async def list_rc_accounts(self, /, start: str, limit: int) -> condenser_api.ListRcAccounts:
        raise NotImplementedError

    @api
    async def list_rc_direct_delegations(
        self, /, start: tuple[str, str], limit: int
    ) -> condenser_api.ListRcDirectDelegations:
        raise NotImplementedError
