from __future__ import annotations

from typing import TYPE_CHECKING, Any

import requests

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from beekeepy._communication.abc.communicator_models import Request, Response
    from beekeepy._communication.settings import CommunicationSettings


class RequestCommunicator(AbstractCommunicator):
    """Provides support for requests library (only synchronous)."""

    def __init__(self, *args: Any, settings: CommunicationSettings, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, **kwargs)
        self.__session: requests.Session | None = None

    async def _async_send(self, request: Request) -> Response:
        raise NotImplementedError

    @property
    def session(self) -> requests.Session:
        if self.__session is None:
            self.__session = requests.Session()
        return self.__session

    def _send(self, request: Request) -> Response:
        try:
            response: requests.Response = self.session.request(
                method=request.method,
                url=request.url.as_string(),
                data=self._encode_data(request.body) if request.body is not None else None,
                headers=request.headers,
                timeout=request.get_timeout(),
            )
            return self._prepare_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                response=self._decode_data(response.content),
            )
        except requests.Timeout as error:
            raise self._construct_timeout_exception(request) from error
        except requests.exceptions.ConnectionError as error:
            raise CommunicationError(url=request.url, request=request.body or "") from error

    def teardown(self) -> None:
        self.session.close()
