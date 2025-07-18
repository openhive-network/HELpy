from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from threading import Thread
from typing import TYPE_CHECKING, Any, Awaitable, TypeGuard, TypeVar, cast

from beekeepy._communication.abc.communicator_models import (
    AsyncCallback,
    AsyncCallbacks,
    AsyncErrorCallback,
    Callbacks,
    ErrorCallback,
    Methods,
    Request,
    Response,
    SyncCallback,
)
from beekeepy._communication.settings import CommunicationSettings
from beekeepy._utilities.settings_holder import SharedSettingsHolder
from beekeepy.exceptions import TimeoutExceededError

if TYPE_CHECKING:
    from beekeepy._communication.url import HttpUrl


T = TypeVar("T")


def default_callback() -> Callbacks:
    return Callbacks()


def default_async_callback() -> AsyncCallbacks:
    return AsyncCallbacks()


class AbstractCommunicator(SharedSettingsHolder[CommunicationSettings], ABC):
    """Provides basic interface for communicators, which can implement communications using different way."""

    # PUBLIC

    def get(self, url: HttpUrl, callbacks: Callbacks | None = None) -> str:
        """Sends to given url given data synchronously as GET."""
        return self.__send(url, "GET", callbacks or default_callback())

    def post(self, url: HttpUrl, data: str | None = None, callbacks: Callbacks | None = None) -> str:
        """Sends to given url given data synchronously as POST."""
        return self.__send(url, "POST", callbacks or default_callback(), data)

    def put(self, url: HttpUrl, data: str | None = None, callbacks: Callbacks | None = None) -> str:
        """Sends to given url given data synchronously as PUT."""
        return self.__send(url, "PUT", callbacks or default_callback(), data)

    def send(self, url: HttpUrl, method: Methods, data: str | None = None, callbacks: Callbacks | None = None) -> str:
        """Sends to given url given data synchronously."""
        return self.__send(url, method, callbacks or default_callback(), data)

    async def async_get(self, url: HttpUrl, callbacks: AsyncCallbacks | None = None) -> str:
        """Sends to given url given data asynchronously as GET."""
        return await self.__async_send(url, "GET", callbacks or default_async_callback())

    async def async_post(self, url: HttpUrl, data: str | None = None, callbacks: AsyncCallbacks | None = None) -> str:
        """Sends to given url given data asynchronously as POST."""
        return await self.__async_send(url, "POST", callbacks or default_async_callback(), data)

    async def async_put(self, url: HttpUrl, data: str | None = None, callbacks: AsyncCallbacks | None = None) -> str:
        """Sends to given url given data asynchronously as PUT."""
        return await self.__async_send(url, "PUT", callbacks or default_async_callback(), data)

    async def async_send(
        self, url: HttpUrl, method: Methods, data: str | None = None, callbacks: AsyncCallbacks | None = None
    ) -> str:
        """Sends to given url given data asynchronously."""
        return await self.__async_send(url, method, callbacks or default_async_callback(), data)

    # ABSTRACT

    @abstractmethod
    def teardown(self) -> None:
        """Called when work with communicator is over."""

    @abstractmethod
    def _send(self, request: Request) -> Response:
        """Sends to given url given data synchronously."""

    @abstractmethod
    async def _async_send(self, request: Request) -> Response:
        """Sends to given url given data asynchronously."""

    # PROTECTED

    @classmethod
    def _encode_data(cls, data: str) -> bytes:
        return data.encode("utf-8")

    @classmethod
    def _decode_data(cls, data: bytes) -> str:
        return data.decode("utf-8")

    @classmethod
    def _default_headers(cls) -> dict[str, str]:
        """Returns headers for json communication."""
        return {"Content-Type": "application/json", "accept": "application/json"}

    def _construct_timeout_exception(self, request: Request) -> TimeoutExceededError:
        return TimeoutExceededError(url=request.url, request=request.body or "", timeout_secs=request.get_timeout())

    def _asyncio_run(self, coro: Awaitable[Any]) -> None:
        thread = Thread(target=asyncio.run, args=(coro,))
        thread.start()
        thread.join()

    def _prepare_request(self, url: HttpUrl, method: Methods, data: str | None = None) -> Request:
        """Default prepare request callback."""
        return Request(
            url=url,
            method=method,
            headers=self._default_headers(),
            body=data,
            timeout=self.settings.timeout,
        )

    def _prepare_response(self, status_code: int, headers: dict[str, str], response: str) -> Response:
        """Default process response callback."""
        return Response(status_code=status_code, headers=headers, body=response)

    # PRIVATE

    def __send(
        self,
        url: HttpUrl,
        method: Methods,
        callbacks: Callbacks,
        data: str | None = None,
    ) -> str:
        request = self._prepare_request(url, method, data)
        if self.__is_available(callbacks.prepare_request):
            request = self.__call_callback(callbacks.prepare_request, Request, callbacks.request_error, request=request)

        try:
            response = self._send(request)
        except Exception as error:
            if self.__is_available(callbacks.communicator_error):
                self.__call_callback(
                    callbacks.communicator_error, type(None), None, request=request, response=None, exception=error
                )
            else:
                raise

        if self.__is_available(callbacks.process_response):
            response = self.__call_callback(
                callbacks.process_response,
                Response,
                callbacks.response_error,
                request=request,
                response=response,
            )

        return response.body

    async def __async_send(
        self,
        url: HttpUrl,
        method: Methods,
        callbacks: AsyncCallbacks,
        data: str | None = None,
    ) -> str:
        request = self._prepare_request(url, method, data)
        if self.__is_available(callbacks.prepare_request):
            request = await self.__call_async_callback(
                cast(AsyncCallback, callbacks.prepare_request),
                Request,
                cast(AsyncErrorCallback | ErrorCallback, callbacks.request_error),
                request=request,
            )

        try:
            response = await self._async_send(request)
        except Exception as error:
            if self.__is_available(callbacks.communicator_error):
                await self.__call_async_callback(
                    cast(AsyncCallback, callbacks.communicator_error),
                    type(None),
                    None,
                    request=request,
                    response=None,
                    exception=error,
                )
            else:
                raise

        if self.__is_available(callbacks.process_response):
            response = await self.__call_async_callback(
                cast(AsyncCallback, callbacks.process_response),
                Response,
                cast(AsyncErrorCallback | ErrorCallback, callbacks.response_error),
                request=request,
                response=response,
            )

        return response.body

    def __call_callback(
        self,
        callback: SyncCallback,
        _: type[T],
        error_callback: ErrorCallback | None = None,
        **kwargs: Any,
    ) -> T:
        """Calls given callback with given arguments."""
        try:
            return cast(T, callback(**kwargs))
        except Exception as error:
            if self.__is_available(error_callback):
                error_callback(**kwargs, exception=error)
            raise

    async def __call_async_callback(
        self,
        callback: AsyncCallback,
        _: type[T],
        error_callback: ErrorCallback | AsyncErrorCallback | None = None,
        **kwargs: Any,
    ) -> T:
        """Calls given callback with given arguments."""
        try:
            if asyncio.iscoroutinefunction(callback):
                return cast(T, await callback(**kwargs))
            return cast(T, callback(**kwargs))
        except Exception as error:
            if self.__is_available(error_callback):
                await self.__call_async_callback(
                    cast(AsyncCallback, error_callback), type(None), None, **kwargs, exception=error
                )
            raise

    def __is_available(self, callback: T | None) -> TypeGuard[T]:
        """Checks if callback is available."""
        return callback is not None
