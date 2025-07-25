from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from loguru import logger as loguru_logger

from beekeepy._apis.abc.api_collection import (
    AbstractAsyncApiCollection,
    AbstractSyncApiCollection,
)
from beekeepy._apis.abc.sendable import AsyncSendable, SyncSendable
from beekeepy._communication import HttpUrl, get_communicator_cls
from beekeepy._remote_handle.settings import RemoteHandleSettings
from beekeepy._utilities.context import SelfContextAsync, SelfContextSync
from beekeepy._utilities.settings_holder import UniqueSettingsHolder
from beekeepy._utilities.stopwatch import Stopwatch
from beekeepy.exceptions import CommunicationError
from schemas.jsonrpc import ExpectResultT, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from loguru import Logger

    from beekeepy._communication import AbstractCommunicator, AbstractOverseer
    from beekeepy._communication.abc.communicator_models import AsyncCallbacks, Callbacks, Methods
    from beekeepy._remote_handle.abc.batch_handle import AsyncBatchHandle, SyncBatchHandle
    from beekeepy.exceptions import Json

RemoteSettingsT = TypeVar("RemoteSettingsT", bound=RemoteHandleSettings)


ApiT = TypeVar("ApiT", bound=AbstractAsyncApiCollection | AbstractSyncApiCollection)


class AbstractHandle(UniqueSettingsHolder[RemoteSettingsT], ABC, Generic[RemoteSettingsT, ApiT]):
    """Provides basic interface for all network handles."""

    def __init__(
        self,
        *args: Any,
        settings: RemoteSettingsT,
        logger: Logger | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs handle to network service.

        Args:
            http_url: http url where, service is available.
            communicator: communicator class to use for communication
        """
        super().__init__(*args, settings=settings, **kwargs)
        self.__logger = self.__configure_logger(logger)
        self.__overseer = self.settings.get_overseer(
            communicator=(self.settings.try_get_communicator_instance() or self._get_recommended_communicator())
        )
        self.__api = self._construct_api()

    @property
    def http_endpoint(self) -> HttpUrl:  # TODO: RESOLVE APPROPRIATE SETTING HANDLE
        """Return endpoint where handle is connected to."""
        assert self.settings.http_endpoint is not None, "Http endpoint shouldn't be None"
        return self.settings.http_endpoint

    @http_endpoint.setter
    def http_endpoint(self, value: HttpUrl) -> None:
        """Set http endpoint."""
        self.logger.debug(f"setting http endpoint to: {value.as_string()}")
        with self.update_settings() as settings:
            settings.http_endpoint = value

    @property
    def apis(self) -> ApiT:
        return self.__api

    @property
    def api(self) -> ApiT:
        return self.__api

    @property
    def _overseer(self) -> AbstractOverseer:
        """Return communicator. Internal only."""
        return self.__overseer

    @property
    def logger(self) -> Logger:
        return self.__logger

    @abstractmethod
    def _get_recommended_communicator(self) -> AbstractCommunicator:
        """Return api collection."""

    @abstractmethod
    def _construct_api(self) -> ApiT:
        """Return api collection."""

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
        return {
            "asynchronous": self._is_synchronous(),
            "handle_target": self._target_service(),
        }

    @classmethod
    def _response_handle(
        cls,
        response: Json | list[Json],
        expected_type: type[ExpectResultT],
        serialization_type: Literal["hf26", "legacy"],
        *,
        is_jsonrpc: bool,
    ) -> JSONRPCResult[ExpectResultT]:
        """Validates and builds response."""
        if is_jsonrpc:
            assert isinstance(response, dict), f"Expected dict as response, got: {response=}"
        else:
            response = {"result": response, "jsonrpc": "2.0", "id": 0}
        serialized_data = get_response_model(expected_type, json.dumps(response), serialization_type)
        assert isinstance(serialized_data, JSONRPCResult)
        return serialized_data

    def __configure_logger(self, logger: Logger | None) -> Logger:
        # credit for lazy=True: https://github.com/Delgan/loguru/issues/402#issuecomment-2028011786
        return (logger or loguru_logger).opt(lazy=True).bind(**self._logger_extras())

    def teardown(self) -> None:
        self._overseer.teardown()

    def _sanitize_data(self, data: Json | list[Json] | str) -> Json | list[Json] | str:
        return data

    def _log_request(self, url: HttpUrl, request: str | None) -> None:
        self.logger.trace(
            "sending to `{}` data: `{}`",
            url.as_string,
            lambda: self._sanitize_data(request or ""),  # to reduce deepcopy
        )

    def _log_response(self, seconds_delta: float, response: Json | list[Json]) -> None:
        self.logger.trace(
            f"got response in {seconds_delta :.5f}s from " + "`{}`: `{}`",
            self.http_endpoint.as_string,
            lambda: self._sanitize_data(response),  # to reduce deepcopy
        )

    def is_testnet(self) -> bool:
        """Returns if handle is connected to testnet."""
        return False

    def _merge_url(self, query_url: HttpUrl | None) -> HttpUrl:
        """Merges given url with path."""
        return HttpUrl.factory(
            address=self.http_endpoint.address,
            port=self.http_endpoint.port,
            path=(query_url or self.http_endpoint).path,
            query=(query_url or self.http_endpoint).query,
            protocol=self.http_endpoint.protocol,
        )

    @classmethod
    def _is_jsonrpc(cls, data: str | None) -> bool:
        """Checks if data is jsonrpc."""
        if data is None:
            return False
        return '"jsonrpc":' in data


class AbstractAsyncHandle(AbstractHandle[RemoteSettingsT, ApiT], SelfContextAsync, AsyncSendable, ABC):
    """Base class for service handlers that uses asynchronous communication."""

    async def _async_send(  # noqa: PLR0913
        self,
        *,
        method: Methods,
        expected_type: type[ExpectResultT],
        serialization_type: Literal["hf26", "legacy"],
        data: str | None = None,
        url: HttpUrl | None = None,
        callbacks: AsyncCallbacks | None = None,
    ) -> JSONRPCResult[ExpectResultT]:
        """Sends data asynchronously to handled service basing on jsonrpc."""
        from beekeepy._utilities.error_logger import ErrorLogger

        final_url = self._merge_url(url)
        self._log_request(final_url, data)
        with Stopwatch() as record, ErrorLogger(self.logger, CommunicationError):
            response = await self._overseer.async_send(
                url=final_url,
                method=method,
                data=data,
                callbacks=callbacks,
            )
        self._log_response(record.seconds_delta, response)
        return self._response_handle(
            response=response,
            expected_type=expected_type,
            serialization_type=serialization_type,
            is_jsonrpc=self._is_jsonrpc(data),
        )

    def _is_synchronous(self) -> bool:
        return False

    def _get_recommended_communicator(self) -> AbstractCommunicator:
        return get_communicator_cls("aiohttp")(settings=self._settings)

    @abstractmethod
    async def batch(self, *, delay_error_on_data_access: bool = False) -> AsyncBatchHandle[Any]:
        """Returns async batch handle."""

    async def _afinally(self) -> None:
        self.teardown()


class AbstractSyncHandle(AbstractHandle[RemoteSettingsT, ApiT], SelfContextSync, SyncSendable, ABC):
    """Base class for service handlers that uses synchronous communication."""

    def _send(  # noqa: PLR0913
        self,
        *,
        method: Methods,
        expected_type: type[ExpectResultT],
        serialization_type: Literal["hf26", "legacy"],
        data: str | None = None,
        url: HttpUrl | None = None,
        callbacks: Callbacks | None = None,
    ) -> JSONRPCResult[ExpectResultT]:
        """Sends data synchronously to handled service basing on jsonrpc."""
        from beekeepy._utilities.error_logger import ErrorLogger

        final_url = self._merge_url(url)
        self._log_request(final_url, data)
        with Stopwatch() as record, ErrorLogger(self.logger, CommunicationError):
            response = self._overseer.send(
                url=final_url,
                method=method,
                data=data,
                callbacks=callbacks,
            )
        self._log_response(record.seconds_delta, response)
        return self._response_handle(
            response=response,
            expected_type=expected_type,
            serialization_type=serialization_type,
            is_jsonrpc=self._is_jsonrpc(data),
        )

    def _is_synchronous(self) -> bool:
        return True

    def _get_recommended_communicator(self) -> AbstractCommunicator:
        return get_communicator_cls("request")(settings=self._settings)

    @abstractmethod
    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[Any]:
        """Returns sync batch handle."""

    def _finally(self) -> None:
        self.teardown()
