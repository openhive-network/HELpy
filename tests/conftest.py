from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

import helpy
from helpy._interfaces.api.abc import AbstractApi, RegisteredApisT


def _convert_test_name_to_directory_name(test_name: str) -> str:
    directory_name = []

    parametrized_test_match = re.match(r"([\w_]+)\[(.*)\]", test_name)
    if parametrized_test_match:
        test_name = f"{parametrized_test_match[1]}_with_parameters_{parametrized_test_match[2]}"

    for character in test_name:
        character_to_append = character
        if not (character_to_append.isalnum() or character_to_append in "-_"):
            character_to_append = f"-0x{ord(character):X}-"

        directory_name.append(character_to_append)

    return "".join(directory_name)


@pytest.fixture(autouse=True)
def working_directory(request: pytest.FixtureRequest) -> Path:
    name_of_directory = _convert_test_name_to_directory_name(request.node.name)
    path_to_generated = request.node.path.parent / name_of_directory
    if path_to_generated.exists():
        shutil.rmtree(path_to_generated)
    path_to_generated.mkdir()
    assert isinstance(path_to_generated, Path), "given object is not Path"
    return path_to_generated


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
    raw_url = request.config.getoption("--hived-http-endpoint")
    assert raw_url is not None
    assert isinstance(raw_url, str)
    return helpy.HttpUrl(raw_url)


@pytest.fixture()
def sync_node(hived_http_endpoint: helpy.HttpUrl) -> helpy.Hived:
    return helpy.Hived(settings=helpy.Settings(http_endpoint=hived_http_endpoint))


@pytest.fixture()
def async_node(hived_http_endpoint: helpy.HttpUrl) -> helpy.AsyncHived:
    return helpy.AsyncHived(settings=helpy.Settings(http_endpoint=hived_http_endpoint))
