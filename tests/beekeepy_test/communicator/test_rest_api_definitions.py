from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from local_tools.beekeepy.simple_api import InputTypeSchema, TestCaller, WitnessesVotersResponseSchema

from beekeepy.handle.remote import RemoteHandleSettings

if TYPE_CHECKING:
    from beekeepy._communication.url import HttpUrl


@pytest.fixture
def caller(hived_http_endpoint: HttpUrl) -> TestCaller:
    """Fixture to create a TestCaller instance."""
    settings = RemoteHandleSettings(http_endpoint=hived_http_endpoint)
    return TestCaller(settings=settings, logger=None)


def validate_type(result: Any, expected_type: type[Any]) -> None:
    assert isinstance(
        result, expected_type
    ), f"Expected result to be a {type(expected_type)}, but got: `{result}` of type `{type(result)}`"


def test_no_args(caller: TestCaller) -> None:
    # ARRANGE & ACT
    result = caller.apis.test_api.last_synced_block()

    # ASSERT
    validate_type(result, int)


def test_pos_args(caller: TestCaller) -> None:
    # ARRANGE & ACT
    result = caller.apis.test_api.input_type("gtg")

    # ASSERT
    validate_type(result, InputTypeSchema)
    assert result.input_type != "invalid_input"


def test_pos_and_keyword_args(caller: TestCaller) -> None:
    # ARRANGE
    expected_amount_of_voters_1 = 10
    expected_amount_of_voters_2 = 5

    # ACT
    result_10_0 = caller.apis.test_api.witnesses_voters("blocktrades", page_size=10)
    result_5_0 = caller.apis.test_api.witnesses_voters("blocktrades", page_size=5)
    result_5_2 = caller.apis.test_api.witnesses_voters("blocktrades", page_size=5, page=2)

    # ASSERT
    validate_type(result_10_0, WitnessesVotersResponseSchema)
    validate_type(result_5_0, WitnessesVotersResponseSchema)
    validate_type(result_5_2, WitnessesVotersResponseSchema)

    assert len(result_10_0.voters) == expected_amount_of_voters_1, "Expected 10 voters in the response"
    assert len(result_5_0.voters) == expected_amount_of_voters_2, "Expected 5 voters in the response"
    assert len(result_5_2.voters) == expected_amount_of_voters_2, "Expected 5 voters in the response for page 2"

    assert result_5_2.voters != result_5_0.voters, "Expected different voters for different pages"
