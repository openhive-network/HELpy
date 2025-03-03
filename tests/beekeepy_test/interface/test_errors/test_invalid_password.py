from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions.detectable import InvalidPasswordError
from helpy.exceptions import InvalidPasswordError as HelpyInvalidPasswordError

if TYPE_CHECKING:
    from beekeepy import Wallet


def test_basic_detection() -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidPasswordError), InvalidPasswordError(wallet_name="wallet"):
        raise HelpyInvalidPasswordError(
            url="",
            request="",
            request_id=None,
        )


def test_test_invalid_private_key(wallet: Wallet) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidPasswordError):
        wallet.unlock(password="invalid")  # noqa: S106
