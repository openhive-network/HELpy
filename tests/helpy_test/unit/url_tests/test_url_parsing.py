from __future__ import annotations

import pytest

from helpy import HttpUrl, WsUrl
from tests.helpy_test.unit.constants import DEFAULT_ADDRESS, DEFAULT_PORT, URL_TYPES


@pytest.mark.parametrize(
    ("input_url", "expected_protocol", "url_type"),
    [
        (f"http://{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "http", HttpUrl),
        (f"ws://{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "ws", WsUrl),
    ],
)
def test_url_parsing_without_expected_protocol(input_url: str, expected_protocol: str, url_type: URL_TYPES) -> None:
    url = url_type(input_url)

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port == DEFAULT_PORT


@pytest.mark.parametrize(
    ("input_url", "expected_protocol", "url_type"),
    [
        (f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "http", HttpUrl),
        (f"{DEFAULT_ADDRESS}:{DEFAULT_PORT}", "ws", WsUrl),
    ],
)
def test_url_parsing_with_expected_protocol(input_url: str, expected_protocol: str, url_type: URL_TYPES) -> None:
    url = url_type(input_url, protocol=expected_protocol)  # type: ignore[arg-type]

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port == DEFAULT_PORT


@pytest.mark.parametrize(
    ("input_url", "expected_protocol", "url_type"),
    [
        (DEFAULT_ADDRESS, "http", HttpUrl),
        (DEFAULT_ADDRESS, "ws", WsUrl),
    ],
)
def test_url_parsing_without_port_given(input_url: str, expected_protocol: str, url_type: URL_TYPES) -> None:
    url = url_type(input_url, protocol=expected_protocol)  # type: ignore[arg-type]

    assert url.protocol == expected_protocol
    assert url.address == DEFAULT_ADDRESS
    assert url.port is None


@pytest.mark.parametrize("url_type", [HttpUrl, WsUrl])
def test_url_parsing_without_address_given(url_type: URL_TYPES) -> None:
    with pytest.raises(ValueError) as exception:  # noqa: PT011
        url_type(f":{DEFAULT_PORT}")

    assert str(exception.value) == "Address was not specified."
