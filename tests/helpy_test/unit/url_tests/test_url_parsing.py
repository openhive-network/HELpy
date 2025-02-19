from __future__ import annotations

import re
from typing import Callable

import pytest

from beekeepy.interfaces import HttpUrl, P2PUrl, WsUrl
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


@pytest.mark.parametrize("url_cls", [HttpUrl, WsUrl, P2PUrl])
@pytest.mark.parametrize("schema_input", [lambda x: x._allowed_protocols()[0], lambda _: None])
def test_schema_auto_apply_in_url(
    schema_input: Callable[[URL_TYPES | type[P2PUrl]], str | None], url_cls: URL_TYPES | type[P2PUrl]
) -> None:
    # ARRANGE
    address = "some-address"
    default_schema = url_cls._allowed_protocols()[0]
    if default_schema:
        default_schema += "://"

    # ACT
    url = url_cls(address, protocol=schema_input(url_cls))  # type: ignore[arg-type]

    # ASSERT
    assert url.as_string() == f"{default_schema}{address}"


@pytest.mark.parametrize("url_cls", [HttpUrl, WsUrl, P2PUrl])
def test_url_schema_validation(url_cls: URL_TYPES | type[P2PUrl]) -> None:
    # ARRANGE
    invalid_proto = "baaaad"

    # ACT & ASSERT
    with pytest.raises(
        ValueError, match=re.escape(f"Unknown protocol: `{invalid_proto}`, allowed: {url_cls._allowed_protocols()}")
    ):
        url_cls("some-address", protocol=invalid_proto)  # type: ignore[arg-type]
