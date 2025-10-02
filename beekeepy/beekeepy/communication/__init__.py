from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._communication.communicator_getter import get_communicator_cls

if TYPE_CHECKING:
    from beekeepy._communication.aiohttp_communicator import AioHttpCommunicator
    from beekeepy._communication.request_communicator import RequestCommunicator

    __all__ = [
        "AioHttpCommunicator",
        "get_communicator_cls",
        "RequestCommunicator",
    ]
else:
    __all__ = [
        "get_communicator_cls",
    ]
