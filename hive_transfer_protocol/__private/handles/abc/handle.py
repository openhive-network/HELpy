from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from hive_transfer_protocol.__private.communication.httpx_communicator import HttpxCommunicator
from hive_transfer_protocol.exceptions import HiveTransferProtocolError
from schemas.__private.hive_factory import HiveResult
from schemas.__private.preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    from hive_transfer_protocol.__private.communication.abc.communicator import AbstractCommunicator
    from hive_transfer_protocol.__private.handles.abc.api_collection import (
        AbstractApiCollection,
    )
    from hive_transfer_protocol.__private.interfaces.url import HttpUrl


ExpectedT = TypeVar("ExpectedT", bound=PreconfiguredBaseModel)


@dataclass
class RequestError(HiveTransferProtocolError):
    """Raised if error field is in the response."""

    send: str
    error: str


class MissingResultError(HiveTransferProtocolError):
    """Raised if response does not have any response."""


class AbstractHandle:
    """Provides basic interface for all network handles."""

    def __init__(self, *, http_url: HttpUrl, communicator: type[AbstractCommunicator] = HttpxCommunicator) -> None:
        self.__http_endpoint = http_url
        self.__communicator = communicator
        self.__api = self._construct_api()

    @property
    def http_endpoint(self) -> HttpUrl:
        """Return endpoint where handle is connected to."""
        return self.__http_endpoint

    @http_endpoint.setter  # type: ignore[attr-defined]  # https://github.com/python/mypy/issues/1465
    def set_http_endpoint(self, value: HttpUrl) -> None:
        """Set http endpoint."""
        self.__http_endpoint = value

    @property
    def api(self) -> AbstractApiCollection[AbstractAsyncHandle] | AbstractApiCollection[AbstractSyncHandle]:
        return self.__api

    @property
    def _communicator(self) -> type[AbstractCommunicator]:
        """Return communicator. Internal only."""
        return self.__communicator

    @abstractmethod
    def _construct_api(self) -> AbstractApiCollection[AbstractAsyncHandle] | AbstractApiCollection[AbstractSyncHandle]:
        """Return api collection."""

    @abstractmethod
    def _clone(self) -> Self:
        """Return clone of itself."""

    def __enter__(self) -> Self:
        """Return clone of itself with immutable address."""
        return self._clone()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Required from context managers, does nothing."""

    @classmethod
    def _response_handle(cls, params: str, response: str, expected_type: type[ExpectedT]) -> HiveResult[ExpectedT]:
        """Validates and builds response."""
        parsed_response = json.loads(response)

        if "error" in parsed_response:
            raise RequestError(send=params, error=parsed_response["error"])

        if "result" not in parsed_response:
            raise MissingResultError

        serialized_data = HiveResult.factory(expected_type, **parsed_response)  # type: ignore[var-annotated]
        assert isinstance(serialized_data, HiveResult)
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


class AbstractAsyncHandle(ABC, AbstractHandle):
    """Base class for service handlers that uses asynchronous communication."""

    async def _async_send(self, *, endpoint: str, params: str, expected_type: type[ExpectedT]) -> HiveResult[ExpectedT]:
        """Sends data asynchronously to handled service basing on jsonrpc."""
        response = await self._communicator.async_send(
            self.http_endpoint, data=self._build_json_rpc_call(method=endpoint, params=params)
        )
        return self._response_handle(params=params, response=response, expected_type=expected_type)


class AbstractSyncHandle(ABC, AbstractHandle):
    """Base class for service handlers that uses synchronous communication."""

    def _send(self, *, endpoint: str, params: str, expected_type: type[ExpectedT]) -> HiveResult[ExpectedT]:
        """Sends data synchronously to handled service basing on jsonrpc."""
        response = self._communicator.send(
            self.http_endpoint, data=self._build_json_rpc_call(method=endpoint, params=params)
        )
        return self._response_handle(params=params, response=response, expected_type=expected_type)
