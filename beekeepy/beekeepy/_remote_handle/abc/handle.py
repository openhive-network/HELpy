from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from loguru import logger

from beekeepy._communication.aiohttp_communicator import AioHttpCommunicator
from beekeepy._communication.request_communicator import RequestCommunicator
from beekeepy._interface.context import SelfContextAsync, SelfContextSync
from beekeepy._interface.settings_holder import UniqueSettingsHolder
from beekeepy._interface.stopwatch import Stopwatch
from beekeepy._remote_handle.build_json_rpc_call import build_json_rpc_call
from beekeepy._remote_handle.settings import Settings
from beekeepy.exceptions import CommunicationError
from schemas.jsonrpc import ExpectResultT, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from loguru import Logger

    from beekeepy._communication.abc.communicator import AbstractCommunicator
    from beekeepy._communication.abc.overseer import AbstractOverseer
    from beekeepy._interface.url import HttpUrl
    from beekeepy._remote_handle.batch_handle import AsyncBatchHandle, SyncBatchHandle
    from beekeepy.exceptions import Json


ApiT = TypeVar("ApiT")


class AbstractHandle(UniqueSettingsHolder[Settings], ABC, Generic[ApiT]):
    """Provides basic interface for all network handles."""

    def __init__(
        self,
        *args: Any,
        settings: Settings,
        **kwargs: Any,
    ) -> None:
        """Constructs handle to network service.

        Args:
            http_url: http url where, service is available.
            communicator: communicator class to use for communication
        """
        super().__init__(*args, settings=settings, **kwargs)
        self.__logger = self.__configure_logger()
        self.__overseer = self.settings.get_overseer(
            communicator=(self.settings.try_get_communicator_instance() or self._get_recommended_communicator())
        )
        self.__api = self._construct_api()

    @property
    def http_endpoint(self) -> HttpUrl:  # TODO: RESOLVE APPROPRIATE SETTING HANDLE
        """Return endpoint where handle is connected to."""
        return self.settings.http_endpoint

    @http_endpoint.setter
    def http_endpoint(self, value: HttpUrl) -> None:
        """Set http endpoint."""
        self.logger.debug(f"setting http endpoint to: {value.as_string()}")
        with self.update_settings() as settings:
            settings.http_endpoint = value

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
        cls, response: Json | list[Json], expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]:
        """Validates and builds response."""
        assert isinstance(response, dict), f"Expected dict as response, got: {response=}"
        serialized_data = get_response_model(expected_type, **response)
        assert isinstance(serialized_data, JSONRPCResult)
        return serialized_data

    def __configure_logger(self) -> Logger:
        # credit for lazy=True: https://github.com/Delgan/loguru/issues/402#issuecomment-2028011786
        return logger.opt(lazy=True).bind(**self._logger_extras())

    def teardown(self) -> None:
        self._overseer.teardown()

    def _sanitize_data(self, data: Json | list[Json] | str) -> Json | list[Json] | str:
        return data

    def _log_request(self, request: str) -> None:
        self.logger.trace(
            "sending to `{}`: `{}`",
            self.http_endpoint.as_string,
            lambda: self._sanitize_data(request),  # to reduce deepcopy
        )

    def _log_response(self, seconds_delta: float, response: Json | list[Json]) -> None:
        self.logger.trace(
            f"got response in {seconds_delta :.5f}s from " + "`{}`: `{}`",
            self.http_endpoint.as_string,
            lambda: self._sanitize_data(response),  # to reduce deepcopy
        )


class AbstractAsyncHandle(AbstractHandle[ApiT], SelfContextAsync, ABC):
    """Base class for service handlers that uses asynchronous communication."""

    async def _async_send(
        self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]:
        """Sends data asynchronously to handled service basing on jsonrpc."""
        from beekeepy._interface.error_logger import ErrorLogger

        request = build_json_rpc_call(method=endpoint, params=params)
        self._log_request(request)
        with Stopwatch() as record, ErrorLogger(self.logger, CommunicationError):
            response = await self._overseer.async_send(self.http_endpoint, data=request)
        self._log_response(record.seconds_delta, response)
        return self._response_handle(response=response, expected_type=expected_type)

    def _is_synchronous(self) -> bool:
        return False

    def _get_recommended_communicator(self) -> AbstractCommunicator:
        return AioHttpCommunicator(settings=self._settings)

    @abstractmethod
    async def batch(self, *, delay_error_on_data_access: bool = False) -> AsyncBatchHandle[Any]:
        """Returns async batch handle."""

    async def _afinally(self) -> None:
        self.teardown()


class AbstractSyncHandle(AbstractHandle[ApiT], SelfContextSync, ABC):
    """Base class for service handlers that uses synchronous communication."""

    def _send(self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]) -> JSONRPCResult[ExpectResultT]:
        """Sends data synchronously to handled service basing on jsonrpc."""
        from beekeepy._interface.error_logger import ErrorLogger

        request = build_json_rpc_call(method=endpoint, params=params)
        self._log_request(request)
        with Stopwatch() as record, ErrorLogger(self.logger, CommunicationError):
            response = self._overseer.send(self.http_endpoint, data=request)
        self._log_response(record.seconds_delta, response)
        return self._response_handle(response=response, expected_type=expected_type)

    def _is_synchronous(self) -> bool:
        return True

    def _get_recommended_communicator(self) -> AbstractCommunicator:
        return RequestCommunicator(settings=self._settings)

    @abstractmethod
    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[Any]:
        """Returns sync batch handle."""

    def _finally(self) -> None:
        self.teardown()
