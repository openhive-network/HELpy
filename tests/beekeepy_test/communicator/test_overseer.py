from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
from local_tools.beekeepy.testing_server import run_simple_server

from beekeepy.communication import (
    CommonOverseer,
    CommunicationSettings,
    StrictOverseer,
    get_communicator_cls,
)
from beekeepy.exceptions import (
    ApiNotFoundError,
    JussiResponseError,
    NullResultError,
    OverseerError,
    UnparsableResponseError,
)

if TYPE_CHECKING:
    from beekeepy.communication import AbstractCommunicator, AbstractOverseer


ERRORS_TO_DETECT: Final[list[tuple[type[OverseerError], str]]] = [
    (
        NullResultError,
        """{"jsonrpc": "2.0", "result": null, "id": 1}""",
    ),
    (
        ApiNotFoundError,
        """{"jsonrpc": "2.0", "error": {"code": -32003, "message":
        "Assert Exception:api_itr != data._registered_apis.end(): Could not find API debug_node_api"
        }, "id": 1}""",
    ),
    (
        JussiResponseError,
        """{"jsonrpc":"2.0","id":null,"error":{"code":-32603,"message":
        "Internal Error","data":{"error_id":"b6384d8c-95ad-4af0-92dc-dd7828d3c707",
        "jussi_request_id":"000312363819934224"}}}""",
    ),
    (UnparsableResponseError, """404: Not Found"""),
]

SYNC_COMMUNICATORS: Final[list[type[AbstractCommunicator]]] = [
    get_communicator_cls("sync"),
]
ASYNC_COMMUNICATORS: Final[list[type[AbstractCommunicator]]] = [
    get_communicator_cls("async"),
]
OVERSEERS: Final[list[type[AbstractOverseer]]] = [CommonOverseer, StrictOverseer]

REQUEST: Final[str] = """{"method": "aaa", "id": 1, "jsonrpc": "2.0"}"""


@pytest.mark.parametrize("error_and_message", ERRORS_TO_DETECT)
@pytest.mark.parametrize("overseer_cls", OVERSEERS)
@pytest.mark.parametrize("communicator", SYNC_COMMUNICATORS)
def test_sync_overseer(
    error_and_message: tuple[type[OverseerError], str],
    overseer_cls: type[AbstractOverseer],
    communicator: type[AbstractCommunicator],
) -> None:
    error, message = error_and_message
    overseer = overseer_cls(communicator=communicator(settings=CommunicationSettings()))
    try:
        with run_simple_server(message) as url, pytest.raises(error):
            overseer.send(url=url, method="POST", data=REQUEST)
    finally:
        overseer.teardown()


@pytest.mark.parametrize("error_and_message", ERRORS_TO_DETECT)
@pytest.mark.parametrize("overseer_cls", OVERSEERS)
@pytest.mark.parametrize("communicator", ASYNC_COMMUNICATORS)
async def test_async_overseer(
    error_and_message: tuple[type[OverseerError], str],
    overseer_cls: type[AbstractOverseer],
    communicator: type[AbstractCommunicator],
) -> None:
    error, message = error_and_message
    overseer = overseer_cls(communicator=communicator(settings=CommunicationSettings()))
    try:
        with run_simple_server(message) as url, pytest.raises(error):
            await overseer.async_send(url=url, method="POST", data=REQUEST)
    finally:
        overseer.teardown()
