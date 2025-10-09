from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [
    "AbstractCommunicator",
    "AbstractOverseer",
    "AioHttpCommunicator",
    "async_is_url_reachable",
    "AsyncCallback",
    "AsyncCallbacks",
    "AsyncErrorCallback",
    "AsyncRequestCallback",
    "AsyncResponseCallback",
    "Callbacks",
    "CommonOverseer",
    "CommunicationSettings",
    "ErrorCallback",
    "get_communicator_cls",
    "Request",
    "RequestCallback",
    "RequestCommunicator",
    "Response",
    "ResponseCallback",
    "rules",
    "StrictOverseer",
    "sync_is_url_reachable",
    "SyncCallback",
]

if TYPE_CHECKING:
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
    from beekeepy._communication.aiohttp_communicator import AioHttpCommunicator
    from beekeepy._communication.communicator_getter import get_communicator_cls
    from beekeepy._communication.is_url_reachable import async_is_url_reachable, sync_is_url_reachable
    from beekeepy._communication.overseers import CommonOverseer, StrictOverseer
    from beekeepy._communication.request_communicator import RequestCommunicator
    from beekeepy._communication.settings import CommunicationSettings


__getattr__ = lazy_module_factory(
    globals(),
    # Translations
    *aggregate_same_import(
        "async_is_url_reachable",
        "sync_is_url_reachable",
        module="beekeepy._communication.is_url_reachable",
    ),
    *aggregate_same_import(
        "AsyncCallback",
        "AsyncCallbacks",
        "AsyncErrorCallback",
        "AsyncRequestCallback",
        "AsyncResponseCallback",
        "Callbacks",
        "ErrorCallback",
        "Request",
        "RequestCallback",
        "Response",
        "ResponseCallback",
        "SyncCallback",
        module="beekeepy._communication.abc.communicator_models",
    ),
    *aggregate_same_import(
        "CommonOverseer",
        "StrictOverseer",
        module="beekeepy._communication.overseers",
    ),
    ("beekeepy._communication", "rules"),
    ("beekeepy._communication.abc.overseer", "AbstractOverseer"),
    ("beekeepy._communication.abc.communicator", "AbstractCommunicator"),
    ("beekeepy._communication.settings", "CommunicationSettings"),
    ("beekeepy._communication.communicator_getter", "get_communicator_cls"),
    ("beekeepy._communication.aiohttp_communicator", "AioHttpCommunicator"),
    ("beekeepy._communication.request_communicator", "RequestCommunicator"),
)
