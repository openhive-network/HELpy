from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, NoReturn

from beekeepy._interface._sanitize import sanitize
from beekeepy._remote_handle.abc.handle import AbstractAsyncHandle, AbstractSyncHandle
from beekeepy._remote_handle.api.api_collection import (
    BeekeeperAsyncApiCollection,
    BeekeeperSyncApiCollection,
)
from beekeepy._remote_handle.api.session_holder import AsyncSessionHolder, SyncSessionHolder
from beekeepy._remote_handle.batch_handle import ApiFactory, AsyncBatchHandle, SyncBatchHandle

if TYPE_CHECKING:
    from typing_extensions import Self

    from beekeepy._communication.abc.overseer import AbstractOverseer
    from beekeepy._interface.url import HttpUrl
    from beekeepy._remote_handle.api import AsyncBeekeeperApi, SyncBeekeeperApi
    from beekeepy.exceptions import Json

_handle_target_service_name = "beekeeper"


def _random_string() -> str:
    return str(uuid.uuid4())


def _raise_acquire_not_possible() -> NoReturn:
    raise RuntimeError("Batch handle has predefined token and should not create its own")


class _SyncSessionBatchHandle(SyncBatchHandle[BeekeeperSyncApiCollection], SyncSessionHolder):
    def __init__(
        self,
        url: HttpUrl,
        overseer: AbstractOverseer,
        api: ApiFactory[Self, BeekeeperSyncApiCollection],
        *args: Any,
        session_token: str,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, overseer, api, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self.set_session_token(session_token)

    def _acquire_session_token(self) -> str:
        _raise_acquire_not_possible()


class _AsyncSessionBatchHandle(AsyncBatchHandle[BeekeeperAsyncApiCollection], AsyncSessionHolder):
    def __init__(
        self,
        url: HttpUrl,
        overseer: AbstractOverseer,
        api: ApiFactory[Self, BeekeeperAsyncApiCollection],
        *args: Any,
        session_token: str,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, overseer, api, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self.set_session_token(session_token)

    async def _acquire_session_token(self) -> str:
        _raise_acquire_not_possible()


class Beekeeper(AbstractSyncHandle[BeekeeperSyncApiCollection], SyncSessionHolder):
    """Synchronous handle for beekeeper service communication."""

    def _construct_api(self) -> BeekeeperSyncApiCollection:
        return BeekeeperSyncApiCollection(owner=self)

    @property
    def api(self) -> SyncBeekeeperApi:  # type: ignore[override]
        return super().api.beekeeper

    def _target_service(self) -> str:
        return _handle_target_service_name

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[BeekeeperSyncApiCollection]:
        return _SyncSessionBatchHandle(
            url=self.http_endpoint,
            overseer=self._overseer,
            api=lambda o: BeekeeperSyncApiCollection(owner=o),
            delay_error_on_data_access=delay_error_on_data_access,
            session_token=self.session.token,
        )

    def _acquire_session_token(self) -> str:
        return self.api.create_session(salt=self._get_salt()).token

    def _get_salt(self) -> str:
        return _random_string()

    def _sanitize_data(self, data: Json | list[Json] | str) -> Json | list[Json] | str:
        return sanitize(data)


class AsyncBeekeeper(AbstractAsyncHandle[BeekeeperAsyncApiCollection], AsyncSessionHolder):
    """Asynchronous handle for beekeeper service communication."""

    def _construct_api(self) -> BeekeeperAsyncApiCollection:
        return BeekeeperAsyncApiCollection(owner=self)

    @property
    def api(self) -> AsyncBeekeeperApi:  # type: ignore[override]
        return super().api.beekeeper

    def _target_service(self) -> str:
        return _handle_target_service_name

    async def batch(self, *, delay_error_on_data_access: bool = False) -> AsyncBatchHandle[BeekeeperAsyncApiCollection]:
        return _AsyncSessionBatchHandle(
            url=self.http_endpoint,
            overseer=self._overseer,
            api=lambda o: BeekeeperAsyncApiCollection(owner=o),
            delay_error_on_data_access=delay_error_on_data_access,
            session_token=(await self.session).token,
        )

    async def _acquire_session_token(self) -> str:
        return (await self.api.create_session(salt=self._get_salt())).token

    def _get_salt(self) -> str:
        return _random_string()

    def _sanitize_data(self, data: Json | list[Json] | str) -> Json | list[Json] | str:
        return sanitize(data)
