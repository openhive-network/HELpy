from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions import WalletWithSuchNameAlreadyExistsError
from helpy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from beekeepy import Session


def test_basic_detection() -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(WalletWithSuchNameAlreadyExistsError), WalletWithSuchNameAlreadyExistsError(wallet_name="aaa"):
        raise ErrorInResponseError(
            url="",
            request="",
            request_id=None,
            response=(
                "Assert Exception:!fc::exists( wallet_file_name ): "
                "Wallet with name: 'aaa' already exists at /some/path/to/aaa.wallet"
            ),
        )


def test_wallet_with_such_name_already_exists(session: Session) -> None:
    # ARRANGE
    session.create_wallet(name="aaa", password="wallet")  # noqa: S106

    # ACT & ASSERT
    with pytest.raises(WalletWithSuchNameAlreadyExistsError):
        session.create_wallet(name="aaa", password="wallet")  # noqa: S106
