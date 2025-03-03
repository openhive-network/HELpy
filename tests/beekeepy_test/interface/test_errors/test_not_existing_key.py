from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy.exceptions.detectable import NotExistingKeyError
from helpy.exceptions import ErrorInResponseError

if TYPE_CHECKING:
    from beekeepy import Session, UnlockedWallet


@pytest.mark.parametrize("wallet_name", ["wallet", None])
@pytest.mark.parametrize(
    "message",
    ["Assert Exception:false: Key not in wallet", "Assert Exception:false: Public key aaa not found in wallet wallet"],
)
def test_basic_detection(message: str, wallet_name: str | None) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(NotExistingKeyError), NotExistingKeyError(public_key="aaa", wallet_name=wallet_name):
        raise ErrorInResponseError(
            url="",
            request="",
            request_id=None,
            response=message,
        )


def test_not_existing_key(session: Session, unlocked_wallet: UnlockedWallet) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(NotExistingKeyError):
        unlocked_wallet.sign_digest(sig_digest="aaa", key="STM8Ya14mz5HiZ3JiEhoad4uoSjuK17fMJgJVVuY4991qrf6tbNdH")

    with pytest.raises(NotExistingKeyError):
        session.sign_digest(sig_digest="aaa", key="STM8Ya14mz5HiZ3JiEhoad4uoSjuK17fMJgJVVuY4991qrf6tbNdH")
