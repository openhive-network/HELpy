from __future__ import annotations

from abc import abstractmethod
from typing import Any

__all__ = ["SyncSessionHolder", "AsyncSessionHolder"]


class SessionHolder:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__session_token: str | None = None
        super().__init__(*args, **kwargs)

    def is_session_token_set(self) -> bool:
        return self.__session_token is not None

    def _set_session_token(self, value: str) -> None:
        self.__session_token = value

    def _clear_session_token(self) -> None:
        self.__session_token = None

    def _check_and_return_session_token(self) -> str:
        assert self.__session_token is not None, "Session token has not been set"
        return self.__session_token


class SyncSessionHolder(SessionHolder):
    @abstractmethod
    def _acquire_session_token(self) -> str:
        ...

    @property
    def session_token(self) -> str:
        if not self.is_session_token_set():
            self._set_session_token(self._acquire_session_token())
        return self._check_and_return_session_token()


class AsyncSessionHolder(SessionHolder):
    @abstractmethod
    async def _acquire_session_token(self) -> str:
        ...

    @property
    async def session_token(self) -> str:
        if not self.is_session_token_set():
            self._set_session_token(await self._acquire_session_token())
        return self._check_and_return_session_token()
