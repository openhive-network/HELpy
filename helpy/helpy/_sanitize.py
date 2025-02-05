from __future__ import annotations

import json
from contextlib import suppress
from copy import deepcopy
from typing import TYPE_CHECKING, Final, TypeVar, overload

if TYPE_CHECKING:
    from helpy.exceptions import Json

mask: Final[str] = "***"
sensitive_keywords: Final[list[str]] = ["wif", "password", "private_key"]
T = TypeVar("T")


def _sanitize_recursively(data: T, *, use_mask_on_str: bool = False) -> T:
    if isinstance(data, str) and use_mask_on_str:
        return mask  # type: ignore[return-value]

    if isinstance(data, dict):
        for key in data:
            data[key] = _sanitize_recursively(data[key], use_mask_on_str=(key in sensitive_keywords))

    if isinstance(data, list):
        return [_sanitize_recursively(item) for item in data]  # type: ignore[return-value]

    return data


@overload
def _sanitize(data: str) -> str: ...


@overload
def _sanitize(data: list[Json]) -> list[Json]: ...


@overload
def _sanitize(data: Json) -> Json: ...


def _sanitize(data: Json | list[Json] | str) -> Json | list[Json] | str:
    if isinstance(data, dict):
        return _sanitize_recursively(data)

    if isinstance(data, list):
        return [(_sanitize(item) if isinstance(item, (dict, list)) else item) for item in data]

    if isinstance(data, str):
        with suppress(json.JSONDecodeError):
            return json.dumps(_sanitize(json.loads(data)))

    return data


def sanitize(data: Json | list[Json] | str) -> Json | list[Json] | str:
    return _sanitize(deepcopy(data))
