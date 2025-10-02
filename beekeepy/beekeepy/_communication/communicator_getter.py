from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from beekeepy.exceptions import UnsupportedCommunicatorTypeError

if TYPE_CHECKING:
    from beekeepy._communication.abc.communicator import AbstractCommunicator

CommunicatorTypes = Literal["async", "sync"]


def get_communicator_cls(communicator: CommunicatorTypes) -> type[AbstractCommunicator]:
    """Returns the appropriate communicator class based on the given type."""
    match communicator:
        case "async":
            from beekeepy._communication.aiohttp_communicator import AioHttpCommunicator

            return AioHttpCommunicator
        case "sync":
            from beekeepy._communication.request_communicator import RequestCommunicator

            return RequestCommunicator
        case _:
            raise UnsupportedCommunicatorTypeError(communicator)
