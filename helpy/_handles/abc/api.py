from __future__ import annotations

import json
import re
from abc import ABC
from collections import defaultdict
from datetime import datetime
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

from helpy._handles.abc.batch_handle import AsyncBatchHandle, SyncBatchHandle
from helpy._handles.abc.handle import (
    AbstractAsyncHandle,
    AbstractSyncHandle,
)
from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.operations.representations.legacy_representation import LegacyRepresentation

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from schemas.jsonrpc import ExpectResultT


P = ParamSpec("P")
SyncHandleT = AbstractSyncHandle | SyncBatchHandle
AsyncHandleT = AbstractAsyncHandle | AsyncBatchHandle
HandleT = TypeVar("HandleT", bound=SyncHandleT | AsyncHandleT)

RegisteredApisT = defaultdict[bool, defaultdict[str, set[str]]]


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
                if isinstance(o, PreconfiguredBaseModel):
                    return o.shallow_dict()
                if isinstance(o, datetime):
                    return PreconfiguredBaseModel.Config.json_encoders[datetime](o)  # type: ignore[no-untyped-call]
                return super().default(o)

        return partial(json.dumps, cls=JsonEncoder)

    def _serialize_params(self, args: Any, kwargs: dict[str, Any]) -> str:
        """Return serialized given params. Can be overloaded."""
        if not self.is_keyword_only():
            return AbstractApi.json_dumps()([args])
        prepared_kwargs = {}
        for key, value in kwargs.items():
            if value is not None:
                prepared_kwargs[key.strip("_")] = value
        return AbstractApi.json_dumps()(prepared_kwargs)

    def _verify_positional_keyword_args(self, args: Any, kwargs: dict[str, Any]) -> None:
        if self.is_keyword_only():
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
        if cls.__is_pytest_running():
            cls.__registered_apis[sync][api].add(endpoint)

    @classmethod
    def _get_registered_methods(cls) -> RegisteredApisT:
        """For tests purposes only; Return __registered_apis."""
        assert cls.__is_pytest_running(), "only available if pytest is running!"
        return cls.__registered_apis

    @classmethod
    def __is_pytest_running(cls) -> bool:
        import pytest_is_running

        return pytest_is_running.is_running()

    def is_keyword_only(self) -> bool:
        return True

    def __init__(self, owner: HandleT) -> None:
        self._owner = owner


class AbstractSyncApi(AbstractApi[SyncHandleT]):
    """Base class for all apis, that provides synchronous endpoints."""

    def __init__(self, owner: SyncHandleT) -> None:
        super().__init__(owner)

    @classmethod
    def _endpoint(cls, wrapped_function: Callable[P, ExpectResultT]) -> Callable[P, ExpectResultT]:
        """Decorator for all api methods in child classes."""
        wrapped_function_name = wrapped_function.__name__
        api_name = cls._get_api_name_from_method(wrapped_function)

        cls._register_method(api=api_name, endpoint=wrapped_function_name, sync=True)

        @wraps(wrapped_function)
        def impl(this: AbstractSyncApi, *args: P.args, **kwargs: P.kwargs) -> ExpectResultT:
            this._verify_positional_keyword_args(args, kwargs)
            return this._owner._send(  # type: ignore[no-any-return, union-attr, misc]
                endpoint=f"{api_name}.{wrapped_function_name}",
                params=this._serialize_params(args=args, kwargs=kwargs),
                expected_type=get_type_hints(wrapped_function)["return"],
            ).result

        return impl  # type: ignore[return-value]


class AbstractAsyncApi(AbstractApi[AsyncHandleT]):
    """Base class for all apis, that provides asynchronous endpoints."""

    def __init__(self, owner: AsyncHandleT) -> None:
        super().__init__(owner)

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
            return (  # type: ignore[no-any-return]
                await this._owner._async_send(  # type: ignore[misc]
                    endpoint=f"{api_name}.{wrapped_function_name}",
                    params=this._serialize_params(args=args, kwargs=kwargs),
                    expected_type=get_type_hints(wrapped_function)["return"],
                )
            ).result

        return impl  # type: ignore[return-value]
