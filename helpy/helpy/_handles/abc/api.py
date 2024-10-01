from __future__ import annotations

import json
import re
from abc import ABC
from collections import defaultdict
from datetime import datetime
from enum import IntEnum
from functools import partial, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    ParamSpec,
    TypeVar,
    get_type_hints,
)

from helpy._handles.abc.handle import (
    AbstractAsyncHandle,
    AbstractSyncHandle,
)
from helpy._handles.batch_handle import AsyncBatchHandle, SyncBatchHandle
from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.fields.serializable import Serializable
from schemas.operations.representations.legacy_representation import LegacyRepresentation

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from schemas.jsonrpc import ExpectResultT


P = ParamSpec("P")
SyncHandleT = AbstractSyncHandle | SyncBatchHandle[Any]
AsyncHandleT = AbstractAsyncHandle | AsyncBatchHandle[Any]
HandleT = TypeVar("HandleT", bound=SyncHandleT | AsyncHandleT)

RegisteredApisT = defaultdict[bool, defaultdict[str, set[str]]]
ApiArgumentsToSerialize = tuple[tuple[Any, ...], dict[str, Any]]


class ApiArgumentSerialization(IntEnum):
    OBJECT = 0
    ARRAY = 1
    DOUBLE_ARRAY = 2


def _convert_pascal_case_to_sneak_case(pascal_case_input: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_case_input).lower()


class AbstractApi(ABC, Generic[HandleT]):
    """Base class for apis."""

    __registered_apis: ClassVar[RegisteredApisT] = defaultdict(lambda: defaultdict(lambda: set()))

    @staticmethod
    def _get_api_name_from_method(method: Callable[P, ExpectResultT] | Callable[P, Awaitable[ExpectResultT]]) -> str:
        """Converts __qualname__ to api name."""
        return _convert_pascal_case_to_sneak_case(method.__qualname__.split(".")[0])

    @classmethod
    def json_dumps(cls) -> Callable[[Any], str]:
        class JsonEncoder(json.JSONEncoder):
            def default(self, o: Any) -> Any:
                if isinstance(o, LegacyRepresentation):
                    return (o.type, o.value)
                if isinstance(o, Serializable):
                    return o.serialize()
                if isinstance(o, PreconfiguredBaseModel):
                    return o.shallow_dict()
                if isinstance(o, datetime):
                    return PreconfiguredBaseModel.Config.json_encoders[datetime](o)  # type: ignore[no-untyped-call]
                return super().default(o)

        return partial(json.dumps, cls=JsonEncoder, ensure_ascii=False)

    def _serialize_params(self, arguments: ApiArgumentsToSerialize) -> str:
        """Return serialized given params. Can be overloaded."""
        json_dumps = AbstractApi.json_dumps()
        if self.argument_serialization() == ApiArgumentSerialization.ARRAY:
            return json_dumps(arguments[0])
        if self.argument_serialization() == ApiArgumentSerialization.DOUBLE_ARRAY:
            return json_dumps([arguments[0]])
        prepared_kwargs = {}
        for key, value in arguments[1].items():
            prepared_kwargs[key.strip("_")] = value
        return json_dumps(prepared_kwargs)

    def _verify_positional_keyword_args(self, args: Any, kwargs: dict[str, Any]) -> None:
        if self.argument_serialization() == ApiArgumentSerialization.OBJECT:
            assert len(args) == 0, "This api allows only keyword arguments; Ex.: foo(a=1, b=2, c=3)"
        else:
            assert len(kwargs) == 0, "This api allows only positional arguments; Ex.: foo(1, 2, 3)"

    @classmethod
    def _api_name(cls) -> str:
        """Return api name. By default uses class name. Can be overloaded."""
        return _convert_pascal_case_to_sneak_case(cls.__name__)

    @classmethod
    def _register_method(cls, *, api: str, endpoint: str, sync: bool) -> None:
        """For tests purposes only; Registers apis in global collection."""
        cls.__registered_apis[sync][api].add(endpoint)

    @classmethod
    def _get_registered_methods(cls) -> RegisteredApisT:
        """Returns registered endpoints."""
        return cls.__registered_apis.copy()

    def _prepare_arguments_for_serialization(self, arguments: ApiArgumentsToSerialize) -> ApiArgumentsToSerialize:
        return arguments

    def argument_serialization(self) -> ApiArgumentSerialization:
        return ApiArgumentSerialization.OBJECT

    def __init__(self, owner: HandleT) -> None:
        self._owner = owner


class AbstractSyncApi(AbstractApi[SyncHandleT]):
    """Base class for all apis, that provides synchronous endpoints."""

    def _additional_arguments_actions(
        self,
        endpoint_name: str,  # noqa: ARG002
        arguments: ApiArgumentsToSerialize,
    ) -> ApiArgumentsToSerialize:
        return self._prepare_arguments_for_serialization(arguments)

    @classmethod
    def _endpoint(cls, wrapped_function: Callable[P, ExpectResultT]) -> Callable[P, ExpectResultT]:
        """Decorator for all api methods in child classes."""
        wrapped_function_name = wrapped_function.__name__
        api_name = cls._get_api_name_from_method(wrapped_function)

        cls._register_method(api=api_name, endpoint=wrapped_function_name, sync=True)

        @wraps(wrapped_function)
        def impl(this: AbstractSyncApi, *args: P.args, **kwargs: P.kwargs) -> ExpectResultT:
            this._verify_positional_keyword_args(args, kwargs)
            endpoint = f"{api_name}.{wrapped_function_name}"
            args_, kwargs_ = this._additional_arguments_actions(endpoint, (args, kwargs))
            return this._owner._send(  # type: ignore[no-any-return, union-attr]
                endpoint=endpoint,
                params=this._serialize_params((args_, kwargs_)),
                expected_type=get_type_hints(wrapped_function)["return"],
            ).result

        return impl  # type: ignore[return-value]


class AbstractAsyncApi(AbstractApi[AsyncHandleT]):
    """Base class for all apis, that provides asynchronous endpoints."""

    async def _additional_arguments_actions(
        self,
        endpoint_name: str,  # noqa: ARG002
        arguments: ApiArgumentsToSerialize,
    ) -> ApiArgumentsToSerialize:
        return self._prepare_arguments_for_serialization(arguments)

    @classmethod
    def _endpoint(
        cls, wrapped_function: Callable[P, Awaitable[ExpectResultT]]
    ) -> Callable[P, Awaitable[ExpectResultT]]:
        """Decorator for all api methods in child classes."""
        wrapped_function_name = wrapped_function.__name__
        api_name = cls._get_api_name_from_method(wrapped_function)  # type: ignore[arg-type]

        cls._register_method(api=api_name, endpoint=wrapped_function_name, sync=False)

        @wraps(wrapped_function)
        async def impl(this: AbstractAsyncApi, *args: P.args, **kwargs: P.kwargs) -> ExpectResultT:
            this._verify_positional_keyword_args(args, kwargs)
            endpoint = f"{api_name}.{wrapped_function_name}"
            args_, kwargs_ = await this._additional_arguments_actions(endpoint, (args, kwargs))
            return (  # type: ignore[no-any-return]
                await this._owner._async_send(  # type: ignore[misc]
                    endpoint=endpoint,
                    params=this._serialize_params((args_, kwargs_)),
                    expected_type=get_type_hints(wrapped_function)["return"],
                )
            ).result

        return impl  # type: ignore[return-value]
