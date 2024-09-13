from __future__ import annotations

from abc import abstractmethod
from typing import Any

from schemas.apis.beekeeper_api import CreateSession

__all__ = ["SyncSessionHolder", "AsyncSessionHolder"]


class Session:
    def __init__(self, token_or_create_session_return: str | CreateSession | Session):
        incoming = token_or_create_session_return
        self.__token = incoming.token if isinstance(incoming, CreateSession | Session) else incoming

    @property
    def token(self) -> str:
        return self.__token


class SessionHolder:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__session: Session | None = None
        super().__init__(*args, **kwargs)

    def is_session_token_set(self) -> bool:
        return self.__session is not None

    def set_session_token(self, value: Session | CreateSession | str) -> None:
        self.__session = Session(value)

    def _clear_session(self) -> None:
        self.__session = None

    def _check_and_return_session(self) -> Session:
        assert self.__session is not None, "Session token has not been set"
        return self.__session


class SyncSessionHolder(SessionHolder):
    @abstractmethod
    def _acquire_session_token(self) -> str: ...

    @property
    def session(self) -> Session:
        if not self.is_session_token_set():
            self.set_session_token(self._acquire_session_token())
        return self._check_and_return_session()


class AsyncSessionHolder(SessionHolder):
    @abstractmethod
    async def _acquire_session_token(self) -> str: ...

    @property
    async def session(self) -> Session:
        if not self.is_session_token_set():
            self.set_session_token(await self._acquire_session_token())
        return self._check_and_return_session()
