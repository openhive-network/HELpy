from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, cast

from helpy._handles.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from helpy._handles.batch_handle import ApiFactory, AsyncBatchHandle, SyncBatchHandle
from helpy._handles.beekeeper.api.api_collection import (
    BeekeeperAsyncApiCollection,
    BeekeeperSyncApiCollection,
)
from helpy._handles.beekeeper.api.session_holder import SessionHolder
from helpy._handles.settings import HandleSettings

if TYPE_CHECKING:
    from typing_extensions import Self

    from helpy._communication.abc.communicator import AbstractCommunicator
    from helpy._interfaces.url import HttpUrl

_handle_target_service_name = "beekeeper"


def _random_string() -> str:
    return str(uuid.uuid4())


def _disabled_api() -> str:
    return ""


class _SyncSessionBatchHandle(SyncBatchHandle[BeekeeperSyncApiCollection], SessionHolder):
    def __init__(
        self,
        url: HttpUrl,
        communicator: AbstractCommunicator,
        api: ApiFactory[Self, BeekeeperSyncApiCollection],
        *args: Any,
        session_token: str,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, communicator, api, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self._set_session_token(session_token)

    def _acquire_session_token(self) -> str:
        raise NotImplementedError


class _AsyncSessionBatchHandle(AsyncBatchHandle[BeekeeperAsyncApiCollection], SessionHolder):
    def __init__(
        self,
        url: HttpUrl,
        communicator: AbstractCommunicator,
        api: ApiFactory[Self, BeekeeperAsyncApiCollection],
        *args: Any,
        session_token: str,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, communicator, api, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self._set_session_token(session_token)

    def _acquire_session_token(self) -> str:
        raise NotImplementedError


class Beekeeper(AbstractSyncHandle, SessionHolder):
    """Synchronous handle for beekeeper service communication."""

    def __init__(
        self,
        *args: Any,
        settings: HandleSettings | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, settings=settings, **kwargs)

    def _clone(self) -> Beekeeper:
        return Beekeeper(http_url=self.http_endpoint, settings=self.settings)

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

    def _acquire_session_token(self) -> str:
        return self.api.beekeeper.create_session(
            notifications_endpoint=self._get_notification_endpoint(), salt=self._get_salt()
        ).token

    def _get_notification_endpoint(self) -> str:
        return _disabled_api()

    def _get_salt(self) -> str:
        return _random_string()


class AsyncBeekeeper(AbstractAsyncHandle, SessionHolder):
    """Asynchronous handle for beekeeper service communication."""

    def _clone(self) -> AsyncBeekeeper:
        return AsyncBeekeeper(http_url=self.http_endpoint, settings=self.settings)

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

    def _acquire_session_token(self) -> str:
        # FIXME: how to make it work both in async and sync mode
        return (
            Beekeeper(settings=HandleSettings(http_endpoint=self.http_endpoint))
            .api.beekeeper.create_session(
                notifications_endpoint=self._get_notification_endpoint(), salt=self._get_salt()
            )
            .token
        )

    def _get_notification_endpoint(self) -> str:
        return _disabled_api()

    def _get_salt(self) -> str:
        return _random_string()
