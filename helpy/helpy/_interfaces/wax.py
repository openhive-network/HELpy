from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol

from pydantic import ValidationError

import wax
from helpy._interfaces.asset import Hf26Asset
from helpy.exceptions import HelpyError
from schemas.fields.basic import PublicKey
from schemas.transaction import Transaction, TransactionLegacy

if TYPE_CHECKING:
    from schemas.fields.assets.hbd import AssetHbdHF26
    from schemas.fields.assets.hive import AssetHiveHF26
    from schemas.fields.assets.vests import AssetVestsHF26
    from schemas.fields.compound import Price
    from schemas.fields.hex import Hex
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


def assure_asset_type(
    value: Hf26Asset.AnyT, expected_type: type[Hf26Asset.AssetPredicateT]
) -> Hf26Asset.AssetPredicateT:
    assert isinstance(
        value, expected_type
    ), f"invalid asset type, expected: {expected_type.__name__}, but got: {type(value).__name__}"
    return value


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


def calculate_legacy_sig_digest(transaction: Transaction, chain_id: str) -> str:
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
) -> Hf26Asset.HiveT:
    result = wax.calculate_vests_to_hp(
        vests=__schema_asset_to_wax(vests),
        total_vesting_fund_hive=__schema_asset_to_wax(total_vesting_fund_hive),
        total_vesting_shares=__schema_asset_to_wax(total_vesting_shares),
    )
    return assure_asset_type(__wax_asset_to_schema(result), Hf26Asset.HiveT)


def calculate_hbd_to_hive(hbd: Hf26Asset.HbdT, base: Hf26Asset.AnyT, quote: Hf26Asset.AnyT) -> Hf26Asset.HiveT:
    result = wax.calculate_hbd_to_hive(
        hbd=__schema_asset_to_wax(hbd),
        base=__schema_asset_to_wax(base),
        quote=__schema_asset_to_wax(quote),
    )
    return assure_asset_type(__wax_asset_to_schema(result), Hf26Asset.HiveT)


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


class SecondStepEncryptionCallback(Protocol):
    """
    Protocol that defines a callable for performing the second step of encryption or decryption in the memo process.

    This callable is expected to handle the transformation (encryption or decryption)
    of the memo content, given two public keys and the content to be processed. Optionally,
    a nonce can be provided to add an extra layer of security.

    Parameters:
        from_key (PublicKey): The public key of the sender (used in encryption/decryption).
        to_key (PublicKey): The public key of the recipient (used in encryption/decryption).
        content (str): The memo content to be encrypted or decrypted.
        nonce (int, optional): A nonce value to ensure uniqueness in encryption (default is 0).

    Returns:
        str: The encrypted or decrypted memo content.
    """

    def __call__(self, from_key: PublicKey | str, to_key: PublicKey | str, content: str, nonce: int = 0) -> str: ...


def encrypt_memo(
    content: str,
    main_encryption_key: PublicKey,
    other_encryption_key: PublicKey,
    second_step_callback: SecondStepEncryptionCallback,
) -> str:
    encrypted_memo = second_step_callback(from_key=main_encryption_key, to_key=other_encryption_key, content=content)
    encoded_encrypted_memo: bytes = wax.encode_encrypted_memo(
        encrypted_content=__python_to_cpp_string(encrypted_memo),
        main_encryption_key=__python_to_cpp_string(main_encryption_key),
        other_encryption_key=__python_to_cpp_string(other_encryption_key),
    )
    return __cpp_to_python_string(encoded_encrypted_memo)


def decrypt_memo(content: str, second_step_callback: SecondStepEncryptionCallback) -> str:
    encrypted_memo = wax.decode_encrypted_memo(encoded_memo=__python_to_cpp_string(content))
    return second_step_callback(
        from_key=__cpp_to_python_string(encrypted_memo.main_encryption_key),
        to_key=__cpp_to_python_string(encrypted_memo.other_encryption_key),
        content=__cpp_to_python_string(encrypted_memo.encrypted_content),
    )


def estimate_hive_collateral(
    current_median_history: Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26],
    current_min_history: Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26],
    hbd_amount_to_get: AssetHbdHF26,
) -> Hf26Asset.AnyT:
    hive_collateral = wax.estimate_hive_collateral(
        current_median_history=wax.python_price(
            base=__schema_asset_to_wax(current_median_history.base),
            quote=__schema_asset_to_wax(current_median_history.quote),
        ),
        current_min_history=wax.python_price(
            base=__schema_asset_to_wax(current_min_history.base),
            quote=__schema_asset_to_wax(current_min_history.quote),
        ),
        hbd_amount_to_get=__schema_asset_to_wax(hbd_amount_to_get),
    )
    return __wax_asset_to_schema(hive_collateral)


def collect_signing_keys(
    transaction: Transaction, retrieve_authorities: Callable[[list[bytes]], dict[bytes, wax.python_authorities]]
) -> list[str]:
    return [
        __cpp_to_python_string(key)
        for key in wax.collect_signing_keys(__as_binary_json(transaction), retrieve_authorities)
    ]


def minimize_required_signatures(
    signed_transaction: Transaction,
    chain_id: Hex,
    available_keys: list[PublicKey],
    authorities_map: dict[bytes, wax.python_authorities],
    get_witness_key: Callable[[bytes], bytes],
) -> list[str]:
    python_minimize_required_signatures_data = wax.python_minimize_required_signatures_data(
        chain_id=__python_to_cpp_string(chain_id),
        available_keys=[__python_to_cpp_string(key) for key in available_keys],
        authorities_map=authorities_map,
        get_witness_key=get_witness_key,
    )

    minimized_signatures = wax.minimize_required_signatures(
        __as_binary_json(signed_transaction), python_minimize_required_signatures_data
    )

    return [__cpp_to_python_string(key) for key in minimized_signatures]


def generate_password_based_private_key(account_name: str, role: str, password: str) -> list[str]:
    private_key = wax.generate_password_based_private_key(
        account=__python_to_cpp_string(account_name),
        role=__python_to_cpp_string(role),
        password=__python_to_cpp_string(password),
    )
    return [
        __cpp_to_python_string(private_key.associated_public_key),
        __cpp_to_python_string(private_key.wif_private_key),
    ]


def suggest_brain_key() -> dict[str, str]:
    brain_key = wax.suggest_brain_key()

    return {
        "brain_priv_key": __cpp_to_python_string(brain_key.brain_key),
        "wif_priv_key": __cpp_to_python_string(brain_key.wif_private_key),
        "pub_key": __cpp_to_python_string(brain_key.associated_public_key),
    }


def get_hive_protocol_config(chain_id: str) -> dict[str, str]:
    hive_protocol_config = wax.get_hive_protocol_config(__python_to_cpp_string(chain_id))
    return {__cpp_to_python_string(k): __cpp_to_python_string(v) for k, v in hive_protocol_config.items()}
