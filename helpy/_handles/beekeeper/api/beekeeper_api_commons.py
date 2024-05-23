from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Protocol

from helpy._handles.abc.api import HandleT

if TYPE_CHECKING:
    from helpy._handles.beekeeper.api.session_holder import AsyncSessionHolder, SyncSessionHolder


class CreateSessionActionProtocol(Protocol):
    def __call__(self, endpoint_name: str, *args: Any, **kwargs: Any) -> tuple[list[Any], dict[str, Any]]:
        ...


class BeekeeperApiCommons(Generic[HandleT]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def _token_required(self, endpoint_name: str) -> bool:
        return endpoint_name != "create_session"

    def _verify_is_owner_can_hold_session_token(self, owner: HandleT) -> None:
        assert isinstance(
            owner, self._get_requires_session_holder_type()
        ), f"owner `{owner}` is not able to handle this request"

    @abstractmethod
    def _get_requires_session_holder_type(self) -> type[SyncSessionHolder] | type[AsyncSessionHolder]:
        ...
