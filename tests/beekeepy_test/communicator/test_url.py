from __future__ import annotations

from typing import Any

import pytest

from beekeepy.interfaces import HttpUrl


@pytest.mark.parametrize(
    ("url", "requirements"),
    [
        ("http://example.com", {"protocol": "http", "address": "example.com", "port": None, "path": "", "query": {}}),
        (
            "https://example.com:8080/path?query=1",
            {"protocol": "https", "address": "example.com", "port": 8080, "path": "path", "query": {"query": "1"}},
        ),
        (
            "https://example.com:8080?query=1",
            {"protocol": "https", "address": "example.com", "port": 8080, "path": "", "query": {"query": "1"}},
        ),
        (
            "http://example.com/path/to/file",
            {"protocol": "http", "address": "example.com", "port": None, "path": "path/to/file", "query": {}},
        ),
        (
            "http://localhost:8000/api/v1/resource?param=value",
            {
                "protocol": "http",
                "address": "localhost",
                "port": 8000,
                "path": "api/v1/resource",
                "query": {"param": "value"},
            },
        ),
        (
            HttpUrl("http://example.com/path?query=1"),
            {"protocol": "http", "address": "example.com", "port": None, "path": "path", "query": {"query": "1"}},
        ),
    ],
)
def test_proper_http_endpoint(url: str | HttpUrl, requirements: dict[str, Any]) -> None:
    # ARRANGE & ACT
    http_url = HttpUrl(url)

    # ASSERT
    assert http_url.protocol == requirements["protocol"]
    assert http_url.address == requirements["address"]
    assert http_url.port == requirements["port"]
    assert http_url.path == requirements["path"]
    assert http_url.query == requirements["query"]


@pytest.mark.parametrize(
    "invalid_url",
    [
        "htp://example.com",  # Invalid protocol
        "http://example.com:port",  # Invalid port
        "http://example.com:8080/path?=value",  # Empty query key
        "http://example.com:8080/path?query=1&query2",  # Invalid query format
    ],
)
def test_invalid_http_endpoint(invalid_url: str) -> None:
    # ARRANGE & ACT & ASSERT
    with pytest.raises(ValueError):  # noqa: PT011
        HttpUrl(invalid_url)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (HttpUrl("http://example.com/path?query=1"), "http://example.com/path?query=1"),
        (HttpUrl("https://example.com:8080/path/to/resource"), "https://example.com:8080/path/to/resource"),
        (
            HttpUrl("http://localhost:8000/api/v1/resource?param=value"),
            "http://localhost:8000/api/v1/resource?param=value",
        ),
        (
            HttpUrl("example.com", port=8080, path="api/v1/resource", query={"param": "value"}),
            "http://example.com:8080/api/v1/resource?param=value",
        ),
        (
            HttpUrl("example.com", port=8080, path="api/v1/resource", query={"param": "value"}, protocol="http"),
            "http://example.com:8080/api/v1/resource?param=value",
        ),
        (
            HttpUrl("example.com", port=None, path="api/v1/resource", query={"param": "value"}, protocol="https"),
            "https://example.com/api/v1/resource?param=value",
        ),
        (
            HttpUrl("example.com", port=None, query={"param": "value"}, protocol="https"),
            "https://example.com?param=value",
        ),
        (
            HttpUrl("example.com", port=8000, query={"param": "value"}, protocol="https"),
            "https://example.com:8000?param=value",
        ),
        (
            HttpUrl("api.hive.blog", protocol="https"),
            "https://api.hive.blog",
        ),
    ],
)
def test_serialization(url: HttpUrl, expected: str) -> None:
    # ARRANGE & ACT
    serialized_url = url.as_string()

    # ASSERT
    assert serialized_url == expected
