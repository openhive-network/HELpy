from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from helpy._handles.build_json_rpc_call import build_json_rpc_call
from helpy.exceptions import CommunicationError, NothingToSendError, ResponseNotReadyError
from schemas.jsonrpc import ExpectResultT, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    from helpy._communication.abc.communicator import AbstractCommunicator
    from helpy._interfaces.url import HttpUrl


class _DelayedResponseWrapper:
    def __init__(self, url: HttpUrl, request: str, expected_type: type[ExpectResultT]) -> None:
        super().__setattr__("_url", url)
        super().__setattr__("_request", request)
        super().__setattr__("_response", None)
        super().__setattr__("_exception", None)
        super().__setattr__("_expected_type", expected_type)

    def __check_is_response_available(self) -> None:
        if (exception := super().__getattribute__("_exception")) is not None:
            raise exception
        if self.__get_data() is None:
            raise ResponseNotReadyError

    def __get_data(self) -> Any:
        response = super().__getattribute__("_response")
        if response is None:
            return None

        if isinstance(response, JSONRPCResult):
            return response.result
        return response

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__check_is_response_available()
        setattr(self.__get_data(), __name, __value)

    def __getattr__(self, __name: str) -> Any:
        self.__check_is_response_available()
        return getattr(self.__get_data(), __name)

    def _set_response(self, **kwargs: Any) -> None:
        expected_type = super().__getattribute__("_expected_type")
        response = get_response_model(expected_type, **kwargs)
        assert isinstance(response, JSONRPCResult)
        super().__setattr__("_response", response.result)

    def _set_exception(self, exception: Exception) -> None:
        super().__setattr__("_exception", exception)


@dataclass(kw_only=True)
class _BatchRequestResponseItem:
    request: str
    delayed_result: _DelayedResponseWrapper


class _PostRequestManager:
    def __init__(self, owner: _BatchHandle, batch_objs: list[_BatchRequestResponseItem]) -> None:
        self.__batch = batch_objs
        self.__owner = owner
        self.__responses: list[dict[str, Any]] = []

    def set_responses(self, responses: str) -> None:
        self.__responses = json.loads(responses)

    def __enter__(self) -> Self:
        return self

    def _set_response_or_exception(self, request_id: int, response: dict[str, Any], exception_url: str = "") -> None:
        if "error" in response:
            # creating a new instance so other responses won't be included in the error
            new_error = CommunicationError(
                url=exception_url,
                request=self.__batch[request_id].request,
                response=response,
            )
            if not self.__owner._delay_error_on_data_access:
                raise new_error
            self.__owner._get_batch_delayed_result(request_id)._set_exception(new_error)
        else:
            self.__owner._get_batch_delayed_result(request_id)._set_response(**response)

    def __exit__(
        self, _: type[BaseException] | None, exception: BaseException | None, traceback: TracebackType | None
    ) -> bool | None:
        if exception is None and len(self.__responses):
            assert len(self.__responses) == len(self.__batch), "Invalid amount of responses"
            for response in self.__responses:
                self._set_response_or_exception(request_id=int(response["id"]), response=response)
            return None

        if not isinstance(exception, CommunicationError) and isinstance(exception, BaseException):
            raise exception

        assert exception is not None
        responses_from_error = exception.get_response()

        # There is no response available, set this exception on all delayed results.
        if responses_from_error is None:
            for request_id in range(len(self.__batch)):
                self.__owner._get_batch_delayed_result(request_id)._set_exception(exception)

            if not self.__owner._delay_error_on_data_access:
                raise exception
            return None

        message = f"Invalid error response format: expected list, got {type(responses_from_error)}"
        assert isinstance(responses_from_error, list), message
        assert len(responses_from_error) == len(self.__batch), "Invalid amount of responses_from_error"

        # Some of the responses might be errors, some might be good - set them on delayed results.
        for response in responses_from_error:
            self._set_response_or_exception(
                request_id=int(response["id"]), response=response, exception_url=exception.url
            )

        if not self.__owner._delay_error_on_data_access:
            raise exception
        return None


class _BatchHandle:
    def __init__(
        self,
        url: HttpUrl,
        communicator: AbstractCommunicator,
        *args: Any,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__url = url
        self.__communicator = communicator
        self._delay_error_on_data_access = delay_error_on_data_access

        self.__batch: list[_BatchRequestResponseItem] = []

    def _impl_handle_request(self, endpoint: str, params: str, *, expect_type: type[ExpectResultT]) -> ExpectResultT:
        @dataclass
        class DummyResponse:
            result: Any

        request = build_json_rpc_call(method=endpoint, params=params, id_=len(self.__batch))
        delayed_result = _DelayedResponseWrapper(url=self.__url, request=request, expected_type=expect_type)
        self.__batch.append(_BatchRequestResponseItem(request=request, delayed_result=delayed_result))
        return DummyResponse(result=delayed_result)  # type: ignore[return-value]

    def __sync_evaluate(self) -> None:
        query = self.__prepare_request()

        with _PostRequestManager(self, self.__batch) as mgr:
            mgr.set_responses(self.__communicator.send(url=self.__url, data=query))

    async def __async_evaluate(self) -> None:
        query = self.__prepare_request()

        with _PostRequestManager(self, self.__batch) as mgr:
            mgr.set_responses(await self.__communicator.async_send(url=self.__url, data=query))

    def __prepare_request(self) -> str:
        return "[" + ",".join([x.request for x in self.__batch]) + "]"

    def _get_batch_delayed_result(self, request_id: int) -> _DelayedResponseWrapper:
        return self.__batch[request_id].delayed_result

    def __is_anything_to_send(self) -> bool:
        return bool(self.__batch)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        if not self.__is_anything_to_send():
            raise NothingToSendError

        await self.__async_evaluate()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        if not self.__is_anything_to_send():
            raise NothingToSendError

        self.__sync_evaluate()


ApiT = TypeVar("ApiT")
OwnerT = TypeVar("OwnerT")


ApiFactory = Callable[[OwnerT], ApiT]


class SyncBatchHandle(_BatchHandle, Generic[ApiT]):
    def __init__(
        self,
        url: HttpUrl,
        communicator: AbstractCommunicator,
        api: ApiFactory[Self, ApiT],
        *args: Any,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, communicator, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self.api: ApiT = api(self)

    def _send(self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]) -> JSONRPCResult[ExpectResultT]:
        return self._impl_handle_request(endpoint, params, expect_type=expected_type)  # type: ignore[arg-type]


class AsyncBatchHandle(_BatchHandle, Generic[ApiT]):
    def __init__(
        self,
        url: HttpUrl,
        communicator: AbstractCommunicator,
        api: ApiFactory[Self, ApiT],
        *args: Any,
        delay_error_on_data_access: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, communicator, *args, delay_error_on_data_access=delay_error_on_data_access, **kwargs)
        self.api: ApiT = api(self)

    async def _async_send(
        self, *, endpoint: str, params: str, expected_type: type[ExpectResultT]
    ) -> JSONRPCResult[ExpectResultT]:
        return self._impl_handle_request(endpoint, params, expect_type=expected_type)  # type: ignore[arg-type]
