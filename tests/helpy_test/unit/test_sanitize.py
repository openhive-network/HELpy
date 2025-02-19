from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

import pytest

from beekeepy.interfaces import mask, sanitize

if TYPE_CHECKING:
    from beekeepy.exceptions import Json

text_to_remove: Final[str] = "brzeczyszczykiewicz"


def extend(data: Json) -> tuple[str, Json, Json, list[Json], list[Json]]:
    return (json.dumps(data), data, {"result": data}, [data], [data, data, data])


@pytest.mark.parametrize(
    "data",
    [
        *extend({"password": text_to_remove}),
        *extend({"a": [{"wif": text_to_remove}]}),
        *extend({"b": {"private_key": text_to_remove}}),
    ],
)
def test_sanitize(data: Json | list[Json] | str) -> None:
    # ARRANGE, ACT
    sanitized_data = str(sanitize(data=data))

    # ASSERT
    assert text_to_remove not in sanitized_data, f"`{text_to_remove}` not removed from: `{sanitized_data}`"
    assert mask in sanitized_data, f"`{mask}` not found in: `{sanitized_data}`"
