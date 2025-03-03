from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions.detectable import InvalidPrivateKeyError
from helpy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from beekeepy import UnlockedWallet


def test_basic_detection() -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidPrivateKeyError), InvalidPrivateKeyError(wifs="aaa"):
        raise ErrorInResponseError(
            url="",
            request="",
            request_id=None,
            response="Assert Exception:false: Key can't be constructed",
        )


def test_invalid_private_key(unlocked_wallet: UnlockedWallet) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidPrivateKeyError):
        unlocked_wallet.import_key(private_key="key" * 17)
