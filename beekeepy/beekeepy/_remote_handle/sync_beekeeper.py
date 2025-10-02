from __future__ import annotations

from typing import TYPE_CHECKING, Any

from beekeepy._apis.abc.session_holder import (
    SyncSessionHolder,
)
from beekeepy._apis.beekeeper_api import (
    BeekeeperSyncApiCollection,
    SyncBeekeeperApi,
)
from beekeepy._remote_handle.abc.batch_handle import ApiFactory, SyncBatchHandle
from beekeepy._remote_handle.abc.handle import AbstractSyncHandle, RemoteSettingsT
from beekeepy._remote_handle.commons import (
    handle_target_service_name,
    raise_acquire_not_possible,
    random_string,
)
from beekeepy._utilities.sanitize import sanitize

if TYPE_CHECKING:
    from typing_extensions import Self

    from beekeepy._communication.abc.overseer import AbstractOverseer
    from beekeepy._communication.url import HttpUrl
    from beekeepy.exceptions import Json


class _SyncSessionBatchHandle(SyncBatchHandle[BeekeeperSyncApiCollection], SyncSessionHolder):
    def __init__(  # noqa: PLR0913
        self,
        url: HttpUrl,
        overseer: AbstractOverseer,
        api: ApiFactory[Self, BeekeeperSyncApiCollection],
        *args: Any,
        session_token: str,
        delay_error_on_data_access: bool = False,
        is_testnet: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            url,
            overseer,
            api,
            *args,
            delay_error_on_data_access=delay_error_on_data_access,
            is_testnet=is_testnet,
            **kwargs,
        )
        self.set_session_token(session_token)

    def _acquire_session_token(self) -> str:
        raise_acquire_not_possible()


class Beekeeper(AbstractSyncHandle[RemoteSettingsT, BeekeeperSyncApiCollection], SyncSessionHolder):
    """Synchronous handle for beekeeper service communication."""

    def _construct_api(self) -> BeekeeperSyncApiCollection:
        return BeekeeperSyncApiCollection(owner=self)

    @property
    def apis(self) -> BeekeeperSyncApiCollection:
        return super().api

    @property
    def api(self) -> SyncBeekeeperApi:  # type: ignore[override]
        return self.apis.beekeeper

    def _target_service(self) -> str:
        return handle_target_service_name

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[BeekeeperSyncApiCollection]:
        return _SyncSessionBatchHandle(
            url=self.http_endpoint,
            overseer=self._overseer,
            api=lambda o: BeekeeperSyncApiCollection(owner=o),
            delay_error_on_data_access=delay_error_on_data_access,
            session_token=self.session.token,
            is_testnet=self.is_testnet(),
        )

    def _acquire_session_token(self) -> str:
        return self.api.create_session(salt=self._get_salt()).token

    def _get_salt(self) -> str:
        return random_string()

    def _sanitize_data(self, data: Json | list[Json] | str) -> Json | list[Json] | str:
        return sanitize(data)


SyncBeekeeperTemplate = Beekeeper
