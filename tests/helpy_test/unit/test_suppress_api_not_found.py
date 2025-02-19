from __future__ import annotations

import json
from typing import cast

import pytest

from beekeepy._communication.rules import ApiNotFound
from beekeepy.exceptions import ApiNotFoundError, GroupedErrorsError
from beekeepy.interfaces import HttpUrl, SuppressApiNotFound


def api_not_found_error(api: str) -> ApiNotFoundError:
    response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32003,
            "message": ("Assert Exception:api_itr != " "data._registered_apis.end(): Could not find API " + api),
        },
        "id": 1,
    }

    result = ApiNotFound(
        url=HttpUrl("0.0.0.0:0"),
        request={"jsonrpc": "2.0", "id": 1, "method": f"{api}.some_method"},
    ).check(response=response, response_raw=json.dumps(response))
    assert len(result) == 1, "Exception has not been generated"
    return cast(ApiNotFoundError, result[0])


@pytest.mark.parametrize(
    "error",
    [
        api_not_found_error(api=api)
        for api in [
            "rc_api",
            "database_api",
            "account_history_api",
            "future_plugin_that_not_exists_yet_api",
        ]
    ],
)
def test_suppress_api_not_found(error: ApiNotFoundError) -> None:
    # ARRANGE & ACT
    with SuppressApiNotFound(error.api) as suppressed:
        raise error from GroupedErrorsError([error])

    # ASSERT
    assert suppressed.errors[0].api == error.api


@pytest.mark.parametrize(
    "error",
    [
        api_not_found_error("debug_node_api"),
        ValueError("some value error"),
    ],
)
def test_suppress_api_not_found_rethrow(error: Exception) -> None:
    # ARRANGE

    # ACT & ASSERT
    with pytest.raises(type(error)), SuppressApiNotFound("rc_api", "database_api") as suppressed:
        raise error from GroupedErrorsError([error])

    assert len(suppressed.errors) == 0, "No errors should be suppressed"
