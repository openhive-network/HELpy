from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from local_tools.beekeepy.generators import generate_wallet_name, generate_wallet_password
from local_tools.beekeepy.models import WalletInfo

from beekeepy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from local_tools.beekeepy.account_credentials import AccountCredentials

    from beekeepy.handle.runnable import Beekeeper


def test_api_close(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    """Test test_api_close will test beekeeper_api.close api call."""
    # ARRANGE
    assert len((beekeeper.api.list_wallets()).wallets) == 1

    # ACT
    beekeeper.api.close(wallet_name=wallet.name)

    # ASSERT
    assert (
        len((beekeeper.api.list_wallets()).wallets) == 0
    ), "After close, there should be no wallets hold by beekeeper."


def test_api_close_import_key_to_closed_wallet(
    beekeeper: Beekeeper, wallet: WalletInfo, keys_to_import: list[AccountCredentials]
) -> None:
    """Test test_api_close_import_key_to_closed_wallet will test possibility of importing key into the closed wallet."""
    # ARRANGE
    beekeeper.api.close(wallet_name=wallet.name)

    # ACT & ASSERT
    with pytest.raises(ErrorInResponseError, match=f"Wallet not found: {wallet.name}"):
        beekeeper.api.import_key(wif_key=keys_to_import[0].private_key, wallet_name=wallet.name)


def test_api_close_double_close(
    beekeeper: Beekeeper, wallet: WalletInfo, keys_to_import: list[AccountCredentials]
) -> None:
    """Test test_api_close_double_close will test possibility of double closing wallet."""
    # ARRANGE
    beekeeper.api.import_key(wif_key=keys_to_import[0].private_key, wallet_name=wallet.name)

    # ACT
    beekeeper.api.close(wallet_name=wallet.name)

    # ASSERT
    with pytest.raises(ErrorInResponseError, match=f"Wallet not found: {wallet.name}"):
        beekeeper.api.close(wallet_name=wallet.name)


def test_api_close_not_existing_wallet(beekeeper: Beekeeper) -> None:
    """Test test_api_close will test possibility of closing not exzisting wallet."""
    # ARRANGE
    wallet = WalletInfo(password=generate_wallet_password(), name=generate_wallet_name())

    # ACT & ASSERT
    with pytest.raises(ErrorInResponseError, match=f"Wallet not found: {wallet.name}"):
        beekeeper.api.close(wallet_name=wallet.name)
