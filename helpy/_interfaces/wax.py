from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

import wax
from helpy._interfaces.asset import Hf26Asset
from helpy.exceptions import HelpyError
from schemas.fields.basic import PublicKey
from schemas.transaction import Transaction, TransactionLegacy

if TYPE_CHECKING:
    from schemas.operations.representations import HF26Representation
    from schemas.operations.representations.representation_value_typevar import RepresentationValueT


class WaxOperationFailedError(HelpyError):
    pass


@dataclass
class RequiredAuthorityCollection:
    posting: set[str]
    active: set[str]
    owner: set[str]

    @property
    def all_accounts(self) -> set[str]:
        result = self.active.copy()
        result.update(self.posting)
        result.update(self.owner)
        return result


def __python_to_cpp_string(value: str) -> bytes:
    return value.encode()


def __cpp_to_python_string(value: bytes) -> str:
    return value.decode()


def __validate_wax_response(response: wax.python_result) -> None:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(__cpp_to_python_string(response.exception_message))


def __schema_asset_to_wax(asset: Hf26Asset.AnyT) -> wax.python_json_asset:
    return wax.python_json_asset(
        amount=__python_to_cpp_string(str(asset.amount)),
        precision=asset.precision,
        nai=__python_to_cpp_string(asset.nai),
    )


def __wax_asset_to_schema(asset: wax.python_json_asset) -> Hf26Asset.AnyT:
    return Hf26Asset.from_nai(
        {
            "amount": int(__cpp_to_python_string(asset.amount)),
            "precision": asset.precision,
            "nai": __cpp_to_python_string(asset.nai),
        }
    )


def __as_binary_json(item: HF26Representation[RepresentationValueT] | Transaction | TransactionLegacy) -> bytes:
    return __python_to_cpp_string(item.json(by_alias=True))


def validate_transaction(transaction: Transaction) -> None:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: HF26Representation[RepresentationValueT]) -> None:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


def calculate_tapos_data(block_id: str) -> wax.python_ref_block_data:
    return wax.get_tapos_data(block_id=__python_to_cpp_string(block_id))


def calculate_sig_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_sig_digest(__as_binary_json(transaction), __python_to_cpp_string(chain_id))
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_transaction_id(transaction: Transaction) -> str:
    result = wax.calculate_transaction_id(__as_binary_json(transaction))
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_legacy_sig_digest(transaction: TransactionLegacy, chain_id: str) -> str:
    result = wax.calculate_legacy_sig_digest(__as_binary_json(transaction), __python_to_cpp_string(chain_id))
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_legacy_transaction_id(transaction: Transaction) -> str:
    result = wax.calculate_legacy_transaction_id(__as_binary_json(transaction))
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_hp_apr(
    head_block_num: int,
    vesting_reward_percent: int,
    virtual_supply: Hf26Asset.AnyT,
    total_vesting_fund_hive: Hf26Asset.HiveT,
) -> str:
    result = wax.calculate_hp_apr(
        head_block_num=head_block_num,
        vesting_reward_percent=vesting_reward_percent,
        virtual_supply=__schema_asset_to_wax(virtual_supply),
        total_vesting_fund_hive=__schema_asset_to_wax(total_vesting_fund_hive),
    )
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_account_hp(
    vests: Hf26Asset.VestT, total_vesting_fund_hive: Hf26Asset.HiveT, total_vesting_shares: Hf26Asset.VestT
) -> Hf26Asset.AnyT:
    result = wax.calculate_account_hp(
        vests=__schema_asset_to_wax(vests),
        total_vesting_fund_hive=__schema_asset_to_wax(total_vesting_fund_hive),
        total_vesting_shares=__schema_asset_to_wax(total_vesting_shares),
    )
    return __wax_asset_to_schema(result)


def calculate_witness_votes_hp(
    votes: int, total_vesting_fund_hive: Hf26Asset.HiveT, total_vesting_shares: Hf26Asset.VestT
) -> Hf26Asset.AnyT:
    result = wax.calculate_witness_votes_hp(
        votes=votes,
        total_vesting_fund_hive=__schema_asset_to_wax(total_vesting_fund_hive),
        total_vesting_shares=__schema_asset_to_wax(total_vesting_shares),
    )
    return __wax_asset_to_schema(result)


def calculate_inflation_rate_for_block(block_num: int) -> str:
    result = wax.calculate_inflation_rate_for_block(block_num=block_num)
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_vests_to_hp(
    vests: Hf26Asset.VestT, total_vesting_fund_hive: Hf26Asset.HiveT, total_vesting_shares: Hf26Asset.VestT
) -> Hf26Asset.AnyT:
    result = wax.calculate_vests_to_hp(
        vests=__schema_asset_to_wax(vests),
        total_vesting_fund_hive=__schema_asset_to_wax(total_vesting_fund_hive),
        total_vesting_shares=__schema_asset_to_wax(total_vesting_shares),
    )
    return __wax_asset_to_schema(result)


def calculate_hbd_to_hive(hbd: Hf26Asset.HbdT, base: Hf26Asset.AnyT, quote: Hf26Asset.AnyT) -> Hf26Asset.HiveT:
    result = wax.calculate_hbd_to_hive(
        hbd=__schema_asset_to_wax(hbd),
        base=__schema_asset_to_wax(base),
        quote=__schema_asset_to_wax(quote),
    )
    asset_result = __wax_asset_to_schema(result)
    assert isinstance(asset_result, Hf26Asset.HiveT), "invalid asset type as result"
    return asset_result


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result


def deserialize_transaction(transaction: bytes) -> Transaction | TransactionLegacy:
    result = wax.deserialize_transaction(transaction)
    __validate_wax_response(result)
    raw_reslt = __cpp_to_python_string(result.result)
    try:
        return Transaction.parse_raw(raw_reslt)
    except ValidationError as err_hf26:
        try:
            return TransactionLegacy.parse_raw(raw_reslt)
        except ValidationError as err_legacy:
            raise ValidationError([[err_hf26, err_legacy]], Transaction) from err_hf26


def calculate_public_key(wif: str) -> PublicKey:
    result = wax.calculate_public_key(__python_to_cpp_string(wif))
    __validate_wax_response(result)
    return PublicKey(__cpp_to_python_string(result.result))


def generate_private_key() -> str:
    result = wax.generate_private_key()
    __validate_wax_response(result)
    return __cpp_to_python_string(result.result)


def calculate_manabar_full_regeneration_time(
    now: int, max_mana: int, current_mana: int, last_update_time: int
) -> datetime.datetime:
    result = wax.calculate_manabar_full_regeneration_time(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return datetime.datetime.fromtimestamp(int(__cpp_to_python_string(result.result)), datetime.timezone.utc)


def calculate_current_manabar_value(now: int, max_mana: int, current_mana: int, last_update_time: int) -> int:
    result = wax.calculate_current_manabar_value(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return int(__cpp_to_python_string(result.result))


def get_transaction_required_authorities(transaction: Transaction) -> RequiredAuthorityCollection:
    result = wax.get_transaction_required_authorities(transaction=__as_binary_json(transaction))

    def to_python_set_str(iterable: set[Any]) -> set[str]:
        return {__cpp_to_python_string(acc) for acc in iterable}

    return RequiredAuthorityCollection(
        owner=to_python_set_str(result.owner_accounts),
        active=to_python_set_str(result.active_accounts),
        posting=to_python_set_str(result.posting_accounts),
    )
