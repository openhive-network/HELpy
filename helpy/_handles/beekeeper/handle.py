from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, cast

from helpy._handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from helpy._handles.batch_handle import AsyncBatchHandle, SyncBatchHandle
from helpy._handles.beekeeper.api.api_collection import (
    BeekeeperAsyncApiCollection,
    BeekeeperSyncApiCollection,
)
from helpy._handles.beekeeper.api.session_holder import SessionHolder

if TYPE_CHECKING:
    from helpy._communication.abc.communicator import AbstractCommunicator
    from helpy._interfaces.url import HttpUrl

_handle_target_service_name = "beekeeper"


def _random_string() -> str:
    return str(uuid.uuid4())


def _dummy_api() -> str:
    # This is dummy url, which always returns 204, otherwise it beekeeper
    # will crash after first send to non existent server (for "")
    return "https://dummyjson.com/http/204"


class Beekeeper(AbstractSyncHandle, SessionHolder):
    """Synchronous handle for beekeeper service communication."""

    def __init__(
        self,
        *args: Any,
        http_url: HttpUrl | None = None,
        communicator: AbstractCommunicator | None = None,
        **kwargs: Any,
    ) -> None:
        self._session_token: str | None = None
        super().__init__(*args, http_url=http_url, communicator=communicator, **kwargs)

    def _clone(self) -> Beekeeper:
        return Beekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperSyncApiCollection:
        return BeekeeperSyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperSyncApiCollection:
        return cast(BeekeeperSyncApiCollection, super().api)

    def _target_service(self) -> str:
        return _handle_target_service_name

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[BeekeeperSyncApiCollection]:
        return SyncBatchHandle(
            url=self.http_endpoint,
            communicator=self._communicator,
            api=lambda o: BeekeeperSyncApiCollection(owner=o),
            delay_error_on_data_access=delay_error_on_data_access,
        )

    def _set_session_token(self) -> None:
        self._SessionHolder__session_token = self.api.beekeeper.create_session(
            notifications_endpoint=self._get_notification_endpoint(), salt=self._get_salt()
        ).token

    def _get_notification_endpoint(self) -> str:
        return _dummy_api()

    def _get_salt(self) -> str:
        return _random_string()


class AsyncBeekeeper(AbstractAsyncHandle, SessionHolder):
    """Asynchronous handle for beekeeper service communication."""

    def _clone(self) -> AsyncBeekeeper:
        return AsyncBeekeeper(http_url=self.http_endpoint, communicator=self._communicator)

    def _construct_api(self) -> BeekeeperAsyncApiCollection:
        return BeekeeperAsyncApiCollection(owner=self)

    @property
    def api(self) -> BeekeeperAsyncApiCollection:
        return cast(BeekeeperAsyncApiCollection, super().api)

    def _target_service(self) -> str:
        return _handle_target_service_name

    def batch(self, *, delay_error_on_data_access: bool = False) -> AsyncBatchHandle[BeekeeperAsyncApiCollection]:
        return AsyncBatchHandle(
            url=self.http_endpoint,
            communicator=self._communicator,
            api=lambda o: BeekeeperAsyncApiCollection(owner=o),
            delay_error_on_data_access=delay_error_on_data_access,
        )

    def _set_session_token(self) -> None:
        # FIXME: how to make it work both in async and sync mode
        self._SessionHolder__session_token = (
            Beekeeper(http_url=self.http_endpoint)
            .api.beekeeper.create_session(
                notifications_endpoint=self._get_notification_endpoint(), salt=self._get_salt()
            )
            .token
        )

    def _get_notification_endpoint(self) -> str:
        return _dummy_api()

    def _get_salt(self) -> str:
        return _random_string()
