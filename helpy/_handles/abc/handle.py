from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger
from typing_extensions import Self

from helpy._communication.httpx_communicator import HttpxCommunicator
from helpy._interfaces.context import ContextAsync, ContextSync
from helpy.exceptions import HelpyError, RequestError
from schemas.jsonrpc import ExpectResultT, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from loguru import Logger

    from helpy._communication.abc.communicator import AbstractCommunicator
    from helpy._handles.abc.api_collection import (
        AbstractApiCollection,
    )
    from helpy._interfaces.url import HttpUrl


class MissingResultError(HelpyError):
    """Raised if response does not have any response."""


class AbstractHandle:
    """Provides basic interface for all network handles."""

    def __init__(
        self,
        *args: Any,
        http_url: HttpUrl | None = None,
        communicator: AbstractCommunicator | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs handle to network service.

        Keyword Arguments:
            http_url -- http url where, service is available.

            communicator -- communicator class to use for communication (default: {HttpxCommunicator})
        """
        super().__init__(*args, **kwargs)
        self.__logger = self.__configure_logger()
        self.__http_endpoint = http_url
        self.__communicator = communicator or HttpxCommunicator()
        self.__api = self._construct_api()

    @property
    def http_endpoint(self) -> HttpUrl:
        """Return endpoint where handle is connected to."""
        assert self.__http_endpoint is not None
        return self.__http_endpoint

    @http_endpoint.setter
    def http_endpoint(self, value: HttpUrl) -> None:
        """Set http endpoint."""
        self.logger.debug(f"setting http endpoint to: {value.as_string()}")
        self.__http_endpoint = value

    @property
    def api(self) -> AbstractApiCollection[AbstractAsyncHandle] | AbstractApiCollection[AbstractSyncHandle]:
        return self.__api

    @property
    def _communicator(self) -> AbstractCommunicator:
        """Return communicator. Internal only."""
        return self.__communicator

    @property
    def logger(self) -> Logger:
        return self.__logger

    @abstractmethod
    def _construct_api(self) -> AbstractApiCollection[AbstractAsyncHandle] | AbstractApiCollection[AbstractSyncHandle]:
        """Return api collection."""

    @abstractmethod
    def _clone(self) -> Self:
        """Return clone of itself."""

    @abstractmethod
    def _is_synchronous(self) -> bool:
        """Returns is handle is asynchronous."""

    @abstractmethod
    def _target_service(self) -> str:
        """Returns name of service that following handle is connecting to."""

    def _logger_extras(self) -> dict[str, Any]:
        """
        Override to pass additional extras to loguru.logger.bind.

        Learn more: https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.bind
        """
        return {"asynchronous": self._is_synchronous(), "handle_target": self._target_service()}

    @classmethod
    def _response_handle(
        cls, params: str, response: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]:
        """Validates and builds response."""
        parsed_response = json.loads(response)

        if "error" in parsed_response:
            raise RequestError(send=params, error=parsed_response["error"])

        if "result" not in parsed_response:
            raise MissingResultError

        serialized_data = get_response_model(expected_type, **parsed_response)
        assert isinstance(serialized_data, JSONRPCResult)
        return serialized_data

    @classmethod
    def _build_json_rpc_call(cls, *, method: str, params: str) -> str:
        """Builds params for jsonrpc call."""
        return (
            """{"id": 0, "jsonrpc": "2.0", "method": \""""
            + method
            + '"'
            + (""", "params":""" + params if params else "")
            + "}"
        )

    def __configure_logger(self) -> Logger:
        return logger.bind(**self._logger_extras())


class AbstractAsyncHandle(ABC, AbstractHandle, ContextAsync[Self]):  # type: ignore[misc]
    """Base class for service handlers that uses asynchronous communication."""

    async def _async_send(
        self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]:
        """Sends data asynchronously to handled service basing on jsonrpc."""
        request = self._build_json_rpc_call(method=endpoint, params=params)
        self.logger.debug(f"sending to `{self.http_endpoint.as_string()}`: `{request}`")
        response = await self._communicator.async_send(self.http_endpoint, data=request)
        self.logger.debug(f"got response from `{self.http_endpoint.as_string()}`: `{response}`")
        return self._response_handle(params=params, response=response, expected_type=expected_type)

    async def _enter(self) -> Self:
        return self._clone()

    async def _finally(self) -> None:
        """Does nothing."""

    def _is_synchronous(self) -> bool:
        return True


class AbstractSyncHandle(ABC, AbstractHandle, ContextSync[Self]):  # type: ignore[misc]
    """Base class for service handlers that uses synchronous communication."""

    def _send(self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]) -> JSONRPCResult[ExpectResultT]:
        """Sends data synchronously to handled service basing on jsonrpc."""
        request = self._build_json_rpc_call(method=endpoint, params=params)
        self.logger.debug(f"sending to `{self.http_endpoint.as_string()}`: `{request}`")
        response = self._communicator.send(self.http_endpoint, data=request)
        self.logger.debug(f"got response from `{self.http_endpoint.as_string()}`: `{response}`")
        return self._response_handle(params=params, response=response, expected_type=expected_type)

    def _enter(self) -> Self:
        return self._clone()

    def _finally(self) -> None:
        """Does nothing."""

    def _is_synchronous(self) -> bool:
        return False
