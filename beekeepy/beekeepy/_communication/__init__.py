from __future__ import annotations

from typing import Literal

from beekeepy._communication import rules
from beekeepy._communication.abc.communicator import AbstractCommunicator
from beekeepy._communication.abc.communicator_models import (
    AsyncCallback,
    AsyncCallbacks,
    AsyncErrorCallback,
    AsyncRequestCallback,
    AsyncResponseCallback,
    Callbacks,
    ErrorCallback,
    Request,
    RequestCallback,
    Response,
    ResponseCallback,
    SyncCallback,
)
from beekeepy._communication.abc.overseer import AbstractOverseer
from beekeepy._communication.overseers import CommonOverseer, StrictOverseer
from beekeepy._communication.settings import CommunicationSettings
from beekeepy._communication.url import AnyUrl, HttpUrl, P2PUrl, Url, WsUrl
from beekeepy.exceptions import UnsupportedCommunicatorTypeError

CommunicatorTypes = Literal["aiohttp", "httpx", "request"]


def get_communicator_cls(communicator: CommunicatorTypes) -> type[AbstractCommunicator]:
    """Returns the appropriate communicator class based on the given type."""
    match communicator:
        case "aiohttp":
            from beekeepy._communication.aiohttp_communicator import AioHttpCommunicator

            return AioHttpCommunicator
        case "httpx":
            from beekeepy._communication.httpx_communicator import HttpxCommunicator

            return HttpxCommunicator
        case "request":
            from beekeepy._communication.request_communicator import RequestCommunicator

            return RequestCommunicator
        case _:
            raise UnsupportedCommunicatorTypeError(communicator)


__all__ = [
    "AbstractCommunicator",
    "AbstractOverseer",
    "AnyUrl",
    "AsyncCallback",
    "AsyncCallbacks",
    "AsyncErrorCallback",
    "AsyncRequestCallback",
    "AsyncResponseCallback",
    "Callbacks",
    "CommonOverseer",
    "CommunicationSettings",
    "ErrorCallback",
    "HttpUrl",
    "OverseerRule",
    "P2PUrl",
    "Request",
    "RequestCallback",
    "get_communicator_cls",
    "Response",
    "ResponseCallback",
    "rules",
    "RulesClassifier",
    "StrictOverseer",
    "SyncCallback",
    "Url",
    "WsUrl",
]
