from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions.detectable import InvalidWalletError
from helpy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from beekeepy import Session


@pytest.mark.parametrize(
    "message",
    [
        "Name of wallet is incorrect. Is empty.",
        "Name of wallet is incorrect. Name: #####. Only alphanumeric and '._-@' chars are allowed",
        "Name of wallet is incorrect. Name: #####. File creation with given name is impossible.",
    ],
    ids=[1, 2, 3],
)
def test_basic_detection(message: str) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidWalletError), InvalidWalletError(wallet_name="#####"):
        raise ErrorInResponseError(
            url="",
            request="",
            request_id=None,
            response=message,
        )


def test_not_existing_key(session: Session) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(InvalidWalletError):
        session.create_wallet(name="####", password="wallet")  # noqa: S106
