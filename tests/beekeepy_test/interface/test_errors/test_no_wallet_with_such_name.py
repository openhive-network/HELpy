from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions.detectable import NoWalletWithSuchNameError
from helpy.exceptions import UnableToOpenWalletError

if TYPE_CHECKING:
    from beekeepy import Session


def test_basic_detection() -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(NoWalletWithSuchNameError), NoWalletWithSuchNameError(wallet_name="some-wallet"):
        raise UnableToOpenWalletError(url="", request="", request_id=None)


def test_no_wallet_with_such_name(session: Session) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(NoWalletWithSuchNameError):
        session.open_wallet(name="not-existing")
