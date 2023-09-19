from __future__ import annotations

import pytest

from helpy import HttpUrl, WsUrl
from tests.unit.constants import DEFAULT_ADDRESS, DEFAULT_PORT, URL_TYPES


@pytest.mark.parametrize(
    ("url", "with_protocol", "expected"),
    [
        (
            HttpUrl(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", protocol="http"),
            True,
            f"http://{DEFAULT_ADDRESS}:{DEFAULT_PORT}",
        ),
        (HttpUrl(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", protocol="http"), False, f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"),
        (HttpUrl(f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"), False, f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}"),
    ],
)
def test_serialization(url: HttpUrl, with_protocol: bool, expected: str) -> None:
    assert url.as_string(with_protocol=with_protocol) == expected


@pytest.mark.parametrize(
    ("input_url", "expected_protocol", "url_type"),
    [
        (DEFAULT_ADDRESS, "http", HttpUrl),
        (DEFAULT_ADDRESS, "ws", WsUrl),
    ],
)
def test_url_serializing_without_port_given(input_url: str, expected_protocol: int, url_type: URL_TYPES) -> None:
    assert (
        url_type(input_url, protocol=expected_protocol).as_string(with_protocol=True) == f"{expected_protocol}://127.0.0.1"  # type: ignore[arg-type]
    )
