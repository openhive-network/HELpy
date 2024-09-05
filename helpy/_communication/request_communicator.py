from __future__ import annotations

from typing import TYPE_CHECKING

import requests

from helpy._communication.abc.communicator import (
    AbstractCommunicator,
)
from helpy.exceptions import CommunicationError

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl


class RequestCommunicator(AbstractCommunicator):
    """Provides support for requests library (only synchronous)."""

    async def async_send(self, url: HttpUrl, data: str) -> str:
        raise NotImplementedError

    def send(self, url: HttpUrl, data: str) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: requests.Response = requests.post(
                    url.as_string(),
                    data=data,
                    headers=self._json_headers(),
                )
                data_received = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except requests.exceptions.ConnectionError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except requests.exceptions.RequestException as error:
                last_exception = error
            self._sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception
