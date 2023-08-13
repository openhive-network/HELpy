from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Literal

from hive_transfer_protocol.__private.handles.abc.api import AbstractAsyncApi
from hive_transfer_protocol.__private.handles.hived.api.database_api.common import DatabaseApiCommons
from hive_transfer_protocol.__private.interfaces.asset import Hf26Asset  # noqa: TCH001
from schemas import database_api  # noqa: TCH001
from schemas.transaction_model.transaction import Hf26Transaction  # noqa: TCH001


class DatabaseApi(AbstractAsyncApi, DatabaseApiCommons):
    api = AbstractAsyncApi._endpoint

    @api
    async def find_account_recovery_requests(self, *, accounts: list[str]) -> database_api.FindAccountRecoveryRequests:
        raise NotImplementedError

    @api
    async def find_accounts(
        self, *, accounts: list[str], delayed_votes_active: bool | None = None
    ) -> database_api.FindAccounts:
        raise NotImplementedError

    @api
    async def find_change_recovery_account_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindChangeRecoveryAccountRequests:
        raise NotImplementedError

    @api
    async def find_collateralized_conversion_requests(
        self, *, account: str
    ) -> database_api.FindCollateralizedConversionRequests:
        raise NotImplementedError

    @api
    async def find_comments(self, *, comments: list[tuple[str, str]]) -> database_api.FindComments:
        raise NotImplementedError

    @api
    async def find_decline_voting_rights_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindDeclineVotingRightsRequests:
        raise NotImplementedError

    @api
    async def find_escrows(self, *, from_: str = "") -> database_api.FindEscrows:
        raise NotImplementedError

    @api
    async def find_hbd_conversion_requests(self, *, account: str) -> database_api.FindHbdConversionRequests:
        raise NotImplementedError

    @api
    async def find_limit_orders(self, *, account: str) -> database_api.FindLimitOrders:
        raise NotImplementedError

    @api
    async def find_owner_histories(self, *, owner: str = "") -> database_api.FindOwnerHistories:
        raise NotImplementedError

    @api
    async def find_proposals(self, *, proposal_ids: list[int]) -> database_api.FindProposals:
        raise NotImplementedError

    @api
    async def find_recurrent_transfers(self, *, from_: str = "") -> database_api.FindRecurrentTransfers:
        raise NotImplementedError

    @api
    async def find_savings_withdrawals(self, *, account: str) -> database_api.FindSavingsWithdrawals:
        raise NotImplementedError

    @api
    async def find_vesting_delegation_expirations(
        self, *, account: str
    ) -> database_api.FindVestingDelegationExpirations:
        raise NotImplementedError

    @api
    async def find_vesting_delegations(self, *, account: str) -> database_api.FindVestingDelegations:
        raise NotImplementedError

    @api
    async def find_withdraw_vesting_routes(
        self, *, account: str, order: DatabaseApi.SORT_TYPES
    ) -> database_api.FindWithdrawVestingRoutes:
        raise NotImplementedError

    @api
    async def find_witnesses(self, *, owners: list[str]) -> database_api.FindWitnesses:
        raise NotImplementedError

    @api
    async def get_active_witnesses(self) -> database_api.GetActiveWitnesses:
        raise NotImplementedError

    @api
    async def get_comment_pending_payouts(
        self, *, comments: list[tuple[str, str]]
    ) -> database_api.GetCommentPendingPayouts:
        raise NotImplementedError

    @api
    async def get_config(self) -> database_api.GetConfig[Hf26Asset.Hive, Hf26Asset.Hbd]:
        raise NotImplementedError

    @api
    async def get_current_price_feed(self) -> database_api.GetCurrentPriceFeed:
        raise NotImplementedError

    @api
    async def get_dynamic_global_properties(
        self,
    ) -> database_api.GetDynamicGlobalProperties[Hf26Asset.Hive, Hf26Asset.Hbd, Hf26Asset.Vests]:
        raise NotImplementedError

    @api
    async def get_feed_history(self) -> database_api.GetFeedHistory[Hf26Asset.Hive, Hf26Asset.Hbd]:
        raise NotImplementedError

    @api
    async def get_hardfork_properties(self) -> database_api.GetHardforkProperties:
        raise NotImplementedError

    @api
    async def get_order_book(
        self, *, limit: int, base: Hf26Asset.Hive, quote: Hf26Asset.Hbd
    ) -> database_api.GetOrderBook:
        raise NotImplementedError

    @api
    async def get_potential_signatures(self, *, trx: Hf26Transaction) -> database_api.GetPotentialSignatures:
        raise NotImplementedError

    @api
    async def get_required_signatures(self, *, trx: Hf26Transaction) -> database_api.GetRequiredSignatures:
        raise NotImplementedError

    @api
    async def get_reward_funds(self) -> database_api.GetRewardFunds:
        raise NotImplementedError

    @api
    async def get_transaction_hex(self, *, trx: Hf26Transaction) -> database_api.GetTransactionHex:
        raise NotImplementedError

    @api
    async def get_version(self) -> database_api.GetVersion:
        raise NotImplementedError

    @api
    async def get_witness_schedule(self) -> database_api.GetWitnessSchedule[Hf26Asset.Hive]:
        raise NotImplementedError

    @api
    async def is_known_transaction(self, *, id_: str) -> database_api.IsKnownTransaction:
        raise NotImplementedError

    @api
    async def list_account_recovery_requests(
        self, *, account: str, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListAccountRecoveryRequests:
        raise NotImplementedError

    @api
    async def list_accounts(
        self,
        *,
        start: str | tuple[str, str] | tuple[datetime, str],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        delayed_votes_active: bool = True,
    ) -> database_api.ListAccounts:
        raise NotImplementedError

    @api
    async def list_change_recovery_account_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListChangeRecoveryAccountRequests:
        raise NotImplementedError

    @api
    async def list_collateralized_conversion_requests(
        self, *, start: str | None, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListCollateralizedConversionRequests:
        raise NotImplementedError

    @api
    async def list_decline_voting_rights_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListDeclineVotingRightsRequests:
        raise NotImplementedError

    @api
    async def list_escrows(
        self, *, start: tuple[str, int] | tuple[bool, datetime, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListEscrows:
        raise NotImplementedError

    @api
    async def list_hbd_conversion_requests(
        self, *, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListHbdConversionRequests:
        raise NotImplementedError

    @api
    async def list_limit_orders(
        self, *, start: tuple[str, int] | tuple[dict[Literal["base", "quote"], Hf26Asset.Hive | Hf26Asset.Hbd], int]
    ) -> database_api.ListLimitOrders:
        raise NotImplementedError

    @api
    async def list_owner_histories(self, *, start: tuple[str, datetime], limit: int) -> database_api.ListOwnerHistories:
        raise NotImplementedError

    @api
    async def list_proposal_votes(
        self,
        *,
        start: list[str],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        order_direction: DatabaseApi.SORT_DIRECTION,
        status: DatabaseApi.PROPOSAL_STATUS,
    ) -> database_api.ListProposalVotes:
        raise NotImplementedError

    @api
    async def list_proposals(
        self,
        *,
        start: list[str] | list[int] | list[datetime],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        order_direction: DatabaseApi.SORT_DIRECTION,
        status: DatabaseApi.PROPOSAL_STATUS,
    ) -> database_api.ListProposals:
        raise NotImplementedError

    @api
    async def list_savings_withdrawals(
        self,
        *,
        start: tuple[int] | tuple[datetime, str, int] | tuple[str, datetime, int],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
    ) -> database_api.ListSavingsWithdrawals:
        raise NotImplementedError

    @api
    async def list_vesting_delegation_expirations(
        self, *, start: tuple[str, datetime, int] | tuple[datetime, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListVestingDelegationExpirations:
        raise NotImplementedError

    @api
    async def list_vesting_delegations(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListVestingDelegations:
        raise NotImplementedError

    @api
    async def list_withdraw_vesting_routes(
        self, *, start: tuple[str, str] | tuple[str, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWithdrawVestingRoutes:
        raise NotImplementedError

    @api
    async def list_witness_votes(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWitnessVotes:
        raise NotImplementedError

    @api
    async def list_witnesses(
        self, *, start: str | tuple[int, str] | tuple[str | int, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWitnesses:
        raise NotImplementedError

    @api
    async def verify_account_authority(
        self, *, account: str, signers: list[str]
    ) -> database_api.VerifyAccountAuthority:
        raise NotImplementedError

    @api
    async def verify_authority(
        self, *, trx: Hf26Transaction, pack: DatabaseApi.PACK_TYPES = "hf26"
    ) -> database_api.VerifyAuthority:
        raise NotImplementedError

    @api
    async def verify_signatures(
        self,
        *,
        hash_: str,
        signatures: list[str],
        required_owner: list[str],
        required_active: list[str],
        required_posting: list[str],
        required_other: list[str],
    ) -> database_api.VerifySignatures:
        raise NotImplementedError
