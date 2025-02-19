from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions import ErrorInResponseError
from beekeepy.interfaces import AccountCredentials
from schemas.fields.basic import PublicKey

if TYPE_CHECKING:
    from local_tools.beekeepy.models import WalletInfo, WalletsGeneratorT

    from beekeepy.handle.runnable import Beekeeper


def test_api_remove_key(
    beekeeper: Beekeeper,
    wallet: WalletInfo,
) -> None:
    """Test test_api_remove_key will test beekeeper_api_remove_key.."""
    # ARRANGE
    for account in AccountCredentials.create_multiple(5):
        beekeeper.api.import_key(wallet_name=wallet.name, wif_key=account.private_key)

        # ACT
        beekeeper.api.remove_key(
            wallet_name=wallet.name,
            public_key=account.public_key,
        )

    # ASSERT
    assert len((beekeeper.api.get_public_keys()).keys) == 0, "There should be no keys left."


def test_api_remove_key_from_locked(beekeeper: Beekeeper, wallet: WalletInfo, account: AccountCredentials) -> None:
    """Test test_api_remove_key_from_locked will try to remove key from locker wallet."""
    # ARRANGE & ACT
    beekeeper.api.lock(wallet_name=wallet.name)

    # ASSERT
    with pytest.raises(ErrorInResponseError, match=f"Wallet is locked: {wallet.name}"):
        beekeeper.api.remove_key(
            wallet_name=wallet.name,
            public_key=account.public_key,
        )


def test_api_remove_key_from_closed(beekeeper: Beekeeper, wallet: WalletInfo, account: AccountCredentials) -> None:
    """Test test_api_remove_key_from_closed will try to remove key from closed wallet."""
    # ARRANGE & ACT
    beekeeper.api.close(wallet_name=wallet.name)

    # ASSERT
    with pytest.raises(ErrorInResponseError, match=f"Wallet not found: {wallet.name}"):
        beekeeper.api.remove_key(
            wallet_name=wallet.name,
            public_key=account.public_key,
        )


def test_api_remove_key_simple_scenario(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_remove_key_simple_scenario will test simple flow of importing and removing keys."""
    # ARRANGE
    wallets = setup_wallets(1, import_keys=True, keys_per_wallet=5, lock=False)
    wallet = wallets[0]
    key_to_remove = wallet.accounts.pop(3)

    # Get keys before removing
    bk_keys_before = (beekeeper.api.get_public_keys()).keys
    bk_pub_keys_before = [pub_key.public_key for pub_key in bk_keys_before]

    # Check if key exist
    assert key_to_remove.public_key in bk_pub_keys_before, "Check if target key exists."

    # ACT
    beekeeper.api.remove_key(
        wallet_name=wallet.name,
        public_key=key_to_remove.public_key,
    )

    # ASSERT
    bk_keys_after = (beekeeper.api.get_public_keys()).keys
    bk_pub_keys_after = [pub_key.public_key for pub_key in bk_keys_after]

    # Check if key was removed
    assert key_to_remove.public_key not in bk_keys_after, "Recently removed key shouldn't not be listed."
    # Check if other keys still exists
    bk_pub_keys_before_copy = bk_pub_keys_before.copy()
    bk_pub_keys_before_copy.remove(PublicKey(key_to_remove.public_key))
    assert sorted(bk_pub_keys_before_copy) == sorted(bk_pub_keys_after), "Check if beekeeper removes only target key."
