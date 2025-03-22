from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger as loguru_logger

from beekeepy._utilities.context import ContextSync

if TYPE_CHECKING:
    from types import TracebackType

    from loguru import Logger


class ErrorLogger(ContextSync[None]):
    def __init__(self, logger: Logger | None = None, *exceptions: type[BaseException]) -> None:
        super().__init__()
        self.__logger = logger or loguru_logger
        self.__exception_whitelist = list(exceptions)

    def _finally(self) -> None:
        return None

    def _enter(self) -> None:
        return None

    def _handle_exception(self, exception: BaseException, tb: TracebackType | None) -> bool:
        if len(self.__exception_whitelist) > 0:
            for whitelisted in self.__exception_whitelist:
                if isinstance(exception, whitelisted):
                    self.__log_exception(exception)
                    break
            return super()._handle_exception(exception, tb)

        self.__log_exception(exception)
        return super()._handle_exception(exception, tb)

    def __log_exception(self, exception: BaseException) -> None:
        self.__logger.info(f"Exception occurred [{type(exception)}]: {exception}")
