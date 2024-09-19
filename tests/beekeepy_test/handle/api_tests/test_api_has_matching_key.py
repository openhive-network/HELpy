from __future__ import annotations

from typing import TYPE_CHECKING

from helpy import AccountCredentials

if TYPE_CHECKING:
    from local_tools.beekeepy.models import WalletInfo

    from beekeepy._handle import Beekeeper


def test_api_has_matching_key(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE
    account = AccountCredentials.create("alice")
    beekeeper.api.import_key(wallet_name=wallet.name, wif_key=account.private_key)

    # ACT
    result = beekeeper.api.has_matching_private_key(wallet_name=wallet.name, public_key=account.public_key)

    # ASSERT
    assert result, "Key should be found in wallet."