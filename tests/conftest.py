from __future__ import annotations

import pytest

import helpy
from helpy._handles.abc.api import AbstractApi, RegisteredApisT


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--hived-http-endpoint", action="store", type=str, help="specifies http_endpoint of reference node"
    )


@pytest.fixture()
def registered_apis() -> RegisteredApisT:
    """Return registered methods."""
    return AbstractApi._get_registered_methods()


@pytest.fixture()
def hived_http_endpoint(request: pytest.FixtureRequest) -> helpy.HttpUrl:
    return helpy.HttpUrl(request.config.getoption("--hived-http-endpoint"), protocol="https")


@pytest.fixture()
def sync_node(hived_http_endpoint: helpy.HttpUrl) -> helpy.Hived:
    return helpy.Hived(http_url=hived_http_endpoint)


@pytest.fixture()
def async_node(hived_http_endpoint: helpy.HttpUrl) -> helpy.AsyncHived:
    return helpy.AsyncHived(http_url=hived_http_endpoint)
