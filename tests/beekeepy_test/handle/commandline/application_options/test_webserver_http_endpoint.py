from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import requests
from local_tools.beekeepy.network import get_port

from beekeepy._executable.arguments.beekeeper_arguments import BeekeeperArguments
from beekeepy._interface.url import HttpUrl
from schemas.apis import beekeeper_api
from schemas.jsonrpc import get_response_model

if TYPE_CHECKING:
    from beekeepy.handle.runnable import Beekeeper


def check_webserver_http_endpoint(*, nofification_endpoint: HttpUrl, webserver_http_endpoint: HttpUrl) -> None:
    """Check if beekeeper is listening on given endpoint."""
    data = {
        "jsonrpc": "2.0",
        "method": "beekeeper_api.create_session",
        "params": {
            "salt": "avocado",
            "notifications_endpoint": nofification_endpoint.as_string(with_protocol=False),
        },
        "id": 1,
    }

    resp = requests.post(webserver_http_endpoint.as_string(), data=json.dumps(data), timeout=10.0)
    assert resp.ok
    resp_json = resp.json()
    get_response_model(beekeeper_api.CreateSession, **resp_json)


@pytest.mark.parametrize(
    "webserver_http_endpoint",
    [
        HttpUrl(f"0.0.0.0:{get_port()}", protocol="http"),
        HttpUrl(f"127.0.0.1:{get_port()}", protocol="http"),
    ],
)
def test_webserver_http_endpoint(beekeeper_not_started: Beekeeper, webserver_http_endpoint: HttpUrl) -> None:
    """Test will check command line flag --webserver_http_endpoint."""
    # ARRANGE & ACT
    beekeeper_not_started.run(
        additional_cli_arguments=BeekeeperArguments(webserver_http_endpoint=webserver_http_endpoint)
    )

    # ASSERT
    assert beekeeper_not_started.settings.notification_endpoint is not None
    check_webserver_http_endpoint(
        nofification_endpoint=beekeeper_not_started.settings.notification_endpoint,
        webserver_http_endpoint=webserver_http_endpoint,
    )
