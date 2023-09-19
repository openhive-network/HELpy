from __future__ import annotations

import json
import re
from abc import ABC
from collections import defaultdict
from functools import wraps
from typing import TYPE_CHECKING, Any, ClassVar, Generic, ParamSpec, TypeVar, get_type_hints

from helpy.__private.handles.abc.handle import (
    AbstractAsyncHandle,
    AbstractSyncHandle,
)
from schemas.__private.preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


P = ParamSpec("P")
R = TypeVar("R", bound=PreconfiguredBaseModel | list[Any] | str | int | None)
HandleT = TypeVar("HandleT", bound=AbstractAsyncHandle | AbstractSyncHandle)

RegisteredApisT = defaultdict[bool, defaultdict[str, set[str]]]


def _convert_pascal_case_to_sneak_case(pascal_case_input: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_case_input).lower()


class AbstractApi(ABC, Generic[HandleT]):
    """Base class for apis."""

    __registered_apis: ClassVar[RegisteredApisT] = defaultdict(lambda: defaultdict(lambda: set()))

    @staticmethod
    def _get_api_name_from_method(method: Callable[P, R] | Callable[P, Awaitable[R]]) -> str:
        """Converts __qualname__ to api name."""
        return _convert_pascal_case_to_sneak_case(method.__qualname__.split(".")[0])

    @classmethod
    def _serialize_params(cls, args: Any, kwargs: dict[str, Any]) -> str:  # noqa: ARG003
        """Return serialized given params. Can be overloaded."""
        return json.dumps(kwargs)

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

    def __init__(self, owner: HandleT) -> None:
        self._owner = owner


class AbstractSyncApi(AbstractApi[AbstractSyncHandle]):
    """Base class for all apis, that provides synchronous endpoints."""

    def __init__(self, owner: AbstractSyncHandle) -> None:
        super().__init__(owner)

    @classmethod
    def _endpoint(cls, wrapped_function: Callable[P, R]) -> Callable[P, R]:
        """Decorator for all api methods in child classes."""
        wrapped_function_name = wrapped_function.__name__
        api_name = cls._get_api_name_from_method(wrapped_function)

        cls._register_method(api=api_name, endpoint=wrapped_function_name, sync=True)

        @wraps(wrapped_function)
        def impl(this: AbstractSyncApi, *args: P.args, **kwargs: P.kwargs) -> R:
            return this._owner._send(  # type: ignore[no-any-return]
                endpoint=f"{api_name}.{wrapped_function_name}",
                params=cls._serialize_params(args=args, kwargs=kwargs),
                expected_type=get_type_hints(wrapped_function)["return"],
            ).result

        return impl  # type: ignore[return-value]


class AbstractAsyncApi(AbstractApi[AbstractAsyncHandle]):
    """Base class for all apis, that provides asynchronous endpoints."""

    def __init__(self, owner: AbstractAsyncHandle) -> None:
        super().__init__(owner)

    @classmethod
    def _endpoint(cls, wrapped_function: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        """Decorator for all api methods in child classes."""
        wrapped_function_name = wrapped_function.__name__
        api_name = cls._get_api_name_from_method(wrapped_function)  # type: ignore[arg-type]

        cls._register_method(api=api_name, endpoint=wrapped_function_name, sync=False)

        @wraps(wrapped_function)
        async def impl(this: AbstractAsyncApi, *args: P.args, **kwargs: P.kwargs) -> R:
            return (  # type: ignore[no-any-return]
                await this._owner._async_send(
                    endpoint=f"{api_name}.{wrapped_function_name}",
                    params=cls._serialize_params(args=args, kwargs=kwargs),
                    expected_type=get_type_hints(wrapped_function)["return"],
                )
            ).result

        return impl  # type: ignore[return-value]
