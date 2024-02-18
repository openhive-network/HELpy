from __future__ import annotations

from abc import abstractmethod
from typing import Any


class SessionHolder:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__session_token: str | None = None
        super().__init__(*args, **kwargs)

    def __is_session_token_set(self) -> bool:
        return self.__session_token is not None

    @abstractmethod
    def _set_session_token(self) -> None:
        ...

    @property
    def session_token(self) -> str:
        if not self.__is_session_token_set():
            self._set_session_token()
        assert self.__session_token is not None
        return self.__session_token
