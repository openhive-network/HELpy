from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from local_tools.beekeepy.models import WalletsGeneratorT

    from beekeepy.handle.runnable import Beekeeper


def test_api_open(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_open will test beekeeper_api.open api call."""
    # ARRANGE
    wallet_path = beekeeper.settings.ensured_working_directory / "wallet-0.wallet"
    assert wallet_path.exists() is False, "Before creation there should be no wallet file."
    wallet = setup_wallets(1, keys_per_wallet=0)[0]

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert wallet_path.exists() is True, "After creation there should be wallet file."
    assert (
        wallet.name == (beekeeper.api.list_wallets()).wallets[0].name
    ), "After creation wallet should be visible in beekeeper."


def test_api_reopen_already_opened(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_reopen_already_opened will try to open already opened wallet."""
    # ARRANGE
    wallet = setup_wallets(1, keys_per_wallet=0)[0]

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."
    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."


def test_api_reopen_closed(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_reopen_closed will try to open closed wallet."""
    # ARRANGE
    wallet = setup_wallets(1, keys_per_wallet=0)[0]

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."

    beekeeper.api.close(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 0, "There should be no wallet opened."

    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be no wallet opened."
