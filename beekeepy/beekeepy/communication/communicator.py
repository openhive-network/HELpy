from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "AbstractCommunicator",
    "AsyncCallback",
    "AsyncCallbacks",
    "AsyncErrorCallback",
    "AsyncRequestCallback",
    "AsyncResponseCallback",
    "Callbacks",
    "CommunicationSettings",
    "ErrorCallback",
    "Request",
    "RequestCallback",
    "Response",
    "ResponseCallback",
    "SyncCallback",
]

if TYPE_CHECKING:
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
    from beekeepy._communication.settings import CommunicationSettings
else:
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        # Translations
        **aggregate_same_import(
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
        AbstractCommunicator="beekeepy._communication.abc.communicator",
        CommunicationSettings="beekeepy._communication.settings",
    )
