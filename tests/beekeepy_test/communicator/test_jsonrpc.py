from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from beekeepy.communication import Callbacks, CommunicationSettings, get_communicator_cls

if TYPE_CHECKING:
    from beekeepy.communication import Request, Response
    from beekeepy.interfaces import HttpUrl

SIMPLE_DATA: Final[str] = """{"id": 0, "jsonrpc": "2.0", "method": "database_api.get_config"}"""
INVALID_DATA: Final[str] = """{"id": 0, "jsonrpc": "2.0", "method": "database_api.get_onfig"}"""


def test_simple_jsonrpc(hived_http_endpoint: HttpUrl) -> None:
    # ARRANGE
    communicator = get_communicator_cls("sync")(settings=CommunicationSettings())

    # ACT
    result = communicator.post(url=hived_http_endpoint, data=SIMPLE_DATA)

    # ASSERT
    assert isinstance(result, str)
    assert len(result) > 0


def test_jsonrpc_with_error(hived_http_endpoint: HttpUrl) -> None:
    # ARRANGE
    communicator = get_communicator_cls("sync")(settings=CommunicationSettings())

    # ACT
    result = communicator.post(url=hived_http_endpoint, data=INVALID_DATA)

    # ASSERT
    assert isinstance(result, str)
    assert len(result) > 0


def test_jsonrpc_with_error_and_callback_reraise(hived_http_endpoint: HttpUrl) -> None:
    # ARRANGE
    error_message: Final[str] = "Invalid response received"
    communicator = get_communicator_cls("sync")(settings=CommunicationSettings())

    def raise_if_error_in_respone(*, request: Request, response: Response) -> None:  # noqa: ARG001
        if "error" in response.body:
            raise ValueError(error_message)

    # ACT & ASSERT
    with pytest.raises(ValueError, match=error_message):
        communicator.post(
            url=hived_http_endpoint,
            data=INVALID_DATA,
            callbacks=Callbacks(process_response=raise_if_error_in_respone),
        )
