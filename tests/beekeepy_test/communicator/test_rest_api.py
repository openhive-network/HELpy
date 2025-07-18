from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
from requests.status_codes import codes

from beekeepy.communication import Callbacks, CommunicationSettings, RequestCommunicator
from beekeepy.interfaces import HttpUrl

if TYPE_CHECKING:
    from beekeepy.communication import Request, Response


@pytest.fixture
def simple_get(hived_http_endpoint: HttpUrl) -> HttpUrl:
    return HttpUrl(
        hived_http_endpoint.address,
        port=hived_http_endpoint.port,
        path="hafbe-api/accounts/gtg",
        protocol=hived_http_endpoint.protocol,
    )


@pytest.fixture
def invalid_get(hived_http_endpoint: HttpUrl) -> HttpUrl:
    return HttpUrl(
        hived_http_endpoint.address,
        port=hived_http_endpoint.port,
        path="hafbe-api/acnts/gtg",
        protocol=hived_http_endpoint.protocol,
    )


def test_simple_restapi(simple_get: HttpUrl) -> None:
    # ARRANGE
    communicator = RequestCommunicator(settings=CommunicationSettings())

    # ACT
    result = communicator.get(url=simple_get)

    # ASSERT
    assert isinstance(result, str)
    assert len(result) > 0


def test_restapi_with_error(invalid_get: HttpUrl) -> None:
    # ARRANGE
    communicator = RequestCommunicator(settings=CommunicationSettings())

    # ACT
    result = communicator.get(url=invalid_get)

    # ASSERT
    assert isinstance(result, str)
    assert len(result) > 0


def test_restapi_with_error_and_callback_reraise(invalid_get: HttpUrl) -> None:
    # ARRANGE
    error_message: Final[str] = "Invalid status code received"
    communicator = RequestCommunicator(settings=CommunicationSettings())

    def raise_if_invalid_status_code(*, request: Request, response: Response) -> None:  # noqa: ARG001
        if response.status_code != codes.ok:
            raise ValueError(error_message)

    # ACT & ASSERT
    with pytest.raises(ValueError, match=error_message):
        communicator.get(
            url=invalid_get,
            callbacks=Callbacks(process_response=raise_if_invalid_status_code),
        )


def test_restapi_with_request_correction(simple_get: HttpUrl, invalid_get: HttpUrl) -> None:
    # ARRANGE
    communicator = RequestCommunicator(settings=CommunicationSettings())

    def fix_url(*, request: Request) -> Request:
        request.url = simple_get
        return request

    # ACT
    result = communicator.get(
        url=invalid_get,
        callbacks=Callbacks(prepare_request=fix_url),
    )

    # ASSERT
    assert isinstance(result, str)
    assert len(result) > 0
