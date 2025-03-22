from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
from local_tools.beekeepy import checkers, waiters

from beekeepy.exceptions import CommunicationError, ErrorInResponseError

if TYPE_CHECKING:
    from beekeepy.handle.runnable import Beekeeper

WRONG_TOKEN: Final[str] = "104fc637d5c32c271bdfdc366af5bfc8f977e2462b01877454cfd1643196bcf1"


def test_api_close_session(beekeeper: Beekeeper) -> None:
    """Test test_api_close_session will test beekeeper_api.close_session api call."""
    # ARRANGE
    token = beekeeper.api.create_session(salt=beekeeper.session.token).token

    # ACT
    beekeeper.api.close_session(token=token)

    # ASSERT
    close_log_entry = '"id":0,"jsonrpc":"2.0","method":"beekeeper_api.close_session",' f'"params":{{"token":"{token}"}}'
    with pytest.raises(
        ErrorInResponseError,
        match=f"A session attached to {token} doesn't exist",
    ):
        beekeeper.api.close_session(token=token)
    assert checkers.check_for_pattern_in_file(
        beekeeper.settings.ensured_working_directory / "stderr.log", close_log_entry
    ), "Log should have information about closing session with specific token created during create_session call."


def test_if_beekeeper_closes_after_last_session_termination(
    beekeeper: Beekeeper,
) -> None:
    """Test test_api_close_session will test if beekeeper closes after closing last session."""
    # ARRANGE & ACT
    beekeeper.api.close_session()
    waiters.wait_for_beekeeper_to_close(beekeeper=beekeeper)

    # ASSERT
    with pytest.raises(CommunicationError, match="no response available"):
        beekeeper.api.list_wallets()

    assert checkers.check_for_pattern_in_file(
        beekeeper.settings.ensured_working_directory / "stderr.log", "exited cleanly"
    ), "Beekeeper should be closed after last session termination."


@pytest.mark.parametrize("create_session", [False, True], ids=["no_session_before", "in_other_session"])
def test_api_close_session_not_existing(create_session: bool, beekeeper: Beekeeper) -> None:
    """Test test_api_close_session_not_existing will test possibility of closing not existing session."""
    # ARRANGE
    if create_session:
        beekeeper.api.create_session(salt="salt")

    # ACT & ASSERT
    beekeeper.set_session_token(WRONG_TOKEN)
    with pytest.raises(ErrorInResponseError, match=f"A session attached to {WRONG_TOKEN} doesn't exist"):
        beekeeper.api.close_session()
