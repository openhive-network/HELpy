from __future__ import annotations

import json
from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from helpy._handles.build_json_rpc_call import build_json_rpc_call
from helpy._interfaces.context import ContextAsync, ContextSync, EnterReturnT
from helpy.exceptions import CommunicationError, JsonT, NothingToSendError, ResponseNotReadyError
from schemas.jsonrpc import ExpectResultT, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    from helpy._communication.abc.communicator import AbstractCommunicator
    from helpy._interfaces.url import HttpUrl


class _DelayedResponseWrapper:
    def __init__(self, url: HttpUrl, request: bytes, expected_type: type[ExpectResultT]) -> None:
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
        assert isinstance(response, JSONRPCResult), "Expected JSONRPCResult, model cannot be found."
        super().__setattr__("_response", response.result)

    def _set_exception(self, exception: BaseException) -> None:
        super().__setattr__("_exception", exception)


@dataclass(kw_only=True)
class _BatchRequestResponseItem:
    request: bytes
    delayed_result: _DelayedResponseWrapper


class _PostRequestManager(ContextSync["_PostRequestManager"]):
    def __init__(self, owner: _BatchHandle[Any], batch_objs: list[_BatchRequestResponseItem]) -> None:
        self.__batch = batch_objs
        self.__owner = owner
        self.__responses: list[dict[str, Any]] = []

    def set_responses(self, responses: str) -> None:
        self.__responses = json.loads(responses)

    def _enter(self) -> _PostRequestManager:
        return self

    def __set_response_or_exception(self, request_id: int, response: dict[str, Any], exception_url: str = "") -> None:
        if "error" in response:
            # creating a new instance so other responses won't be included in the error
            new_error = CommunicationError(
                url=exception_url,
                request=self.__batch[request_id].request,
                response=response,
            )
            self.__owner._get_batch_delayed_result(request_id)._set_exception(new_error)
            if not self.__owner._delay_error_on_data_access:
                raise new_error
        else:
            self.__owner._get_batch_delayed_result(request_id)._set_response(**response)

    def __handle_no_exception_case(self) -> None:
        self.__validate_response_count(self.__responses)
        for response in self.__responses:
            self.__set_response_or_exception(request_id=int(response["id"]), response=response)

    def __handle_exception_and_no_responses_exists(self, exception: BaseException) -> bool:
        for request_id in range(len(self.__batch)):
            self.__owner._get_batch_delayed_result(request_id)._set_exception(exception)

        if not self.__owner._delay_error_on_data_access:
            return False
        return True

    def __handle_exception_and_responses_exists(self, responses: list[JsonT], url: str) -> bool:
        for response in responses:
            self.__set_response_or_exception(request_id=int(response["id"]), response=response, exception_url=url)
        return not self.__owner._delay_error_on_data_access

    def __validate_response_count(self, response: list[JsonT]) -> None:
        message = "Invalid amount of responses_from_error"
        assert len(response) == len(self.__batch), message

    def __handle_exception_case(self, exception: BaseException) -> bool:
        if not isinstance(exception, CommunicationError) and isinstance(exception, BaseException):
            return False

        responses_from_error = exception.get_response()
        if responses_from_error is None:
            return self.__handle_exception_and_no_responses_exists(exception)

        message = f"Invalid error response format: expected list, got {type(responses_from_error)}"
        assert isinstance(responses_from_error, list), message
        self.__validate_response_count(responses_from_error)
        return self.__handle_exception_and_responses_exists(responses_from_error, exception.url)

    def _handle_exception(self, exception: BaseException, __: TracebackType | None) -> bool:
        return self.__handle_exception_case(exception)

    def _handle_no_exception(self) -> None:
        self.__handle_no_exception_case()

    def _finally(self) -> None:
        return None


class _BatchHandle(ContextSync[EnterReturnT], ContextAsync[EnterReturnT], Generic[EnterReturnT], ABC):
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

    def __prepare_request(self) -> bytes:
        return b"[" + b",".join([x.request for x in self.__batch]) + b"]"

    def _get_batch_delayed_result(self, request_id: int) -> _DelayedResponseWrapper:
        return self.__batch[request_id].delayed_result

    def __is_anything_to_send(self) -> bool:
        return bool(self.__batch)

    async def _aenter(self) -> EnterReturnT:
        return self  # type: ignore[return-value]

    def _enter(self) -> EnterReturnT:
        return self  # type: ignore[return-value]

    async def _ahandle_no_exception(self) -> None:
        if not self.__is_anything_to_send():
            raise NothingToSendError

        await self.__async_evaluate()

    def _handle_no_exception(self) -> None:
        if not self.__is_anything_to_send():
            raise NothingToSendError

        self.__sync_evaluate()

    async def _afinally(self) -> None:
        return None

    def _finally(self) -> None:
        return None


ApiT = TypeVar("ApiT")
OwnerT = TypeVar("OwnerT")


ApiFactory = Callable[[OwnerT], ApiT]


class SyncBatchHandle(_BatchHandle["SyncBatchHandle"], Generic[ApiT]):  # type: ignore[type-arg]
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


class AsyncBatchHandle(_BatchHandle["AsyncBatchHandle"], Generic[ApiT]):  # type: ignore[type-arg]
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
