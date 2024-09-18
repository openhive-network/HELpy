from __future__ import annotations

from typing import TYPE_CHECKING

from local_tools.beekeepy.generators import generate_wallet_name, generate_wallet_password
from local_tools.beekeepy.models import WalletInfo

if TYPE_CHECKING:
    from beekeepy._handle import Beekeeper


def test_api_open(beekeeper: Beekeeper) -> None:
    """Test test_api_open will test beekeeper_api.open api call."""
    # ARRANGE
    wallet = WalletInfo(password=generate_wallet_password(), name=generate_wallet_name())
    wallet_path = beekeeper.settings.working_directory / f"{wallet.name}.wallet"
    assert wallet_path.exists() is False, "Before creation there should be no wallet file."
    beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert wallet_path.exists() is True, "After creation there should be wallet file."
    assert (
        wallet.name == (beekeeper.api.list_wallets()).wallets[0].name
    ), "After creation wallet should be visible in beekeeper."


def test_api_reopen_already_opened(beekeeper: Beekeeper) -> None:
    """Test test_api_reopen_already_opened will try to open already opened wallet."""
    # ARRANGE
    wallet = WalletInfo(password=generate_wallet_password(), name=generate_wallet_name())
    beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."
    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."


def test_api_reopen_closed(beekeeper: Beekeeper) -> None:
    """Test test_api_reopen_closed will try to open closed wallet."""
    # ARRANGE
    wallet = WalletInfo(password=generate_wallet_password(), name=generate_wallet_name())
    beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)

    # ACT
    beekeeper.api.open(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be 1 wallet opened."

    beekeeper.api.close(wallet_name=wallet.name)
    assert len((beekeeper.api.list_wallets()).wallets) == 0, "There should be no wallet opened."

    beekeeper.api.open(wallet_name=wallet.name)

    # ASSERT
    assert len((beekeeper.api.list_wallets()).wallets) == 1, "There should be no wallet opened."
