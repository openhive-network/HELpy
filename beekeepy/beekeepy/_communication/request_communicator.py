from __future__ import annotations

from typing import TYPE_CHECKING, Any

import requests

from beekeepy._communication.abc.communicator import (
    AbstractCommunicator,
)
from beekeepy.exceptions import CommunicationError

if TYPE_CHECKING:
    from beekeepy._communication.settings import CommunicationSettings
    from beekeepy._interface.stopwatch import StopwatchResult
    from beekeepy._interface.url import HttpUrl


class RequestCommunicator(AbstractCommunicator):
    """Provides support for requests library (only synchronous)."""

    def __init__(self, *args: Any, settings: CommunicationSettings, **kwargs: Any) -> None:
        super().__init__(*args, settings=settings, **kwargs)
        self.__session: requests.Session | None = None

    async def _async_send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        raise NotImplementedError

    @property
    def session(self) -> requests.Session:
        if self.__session is None:
            self.__session = requests.Session()
        return self.__session

    def _send(self, url: HttpUrl, data: bytes, stopwatch: StopwatchResult) -> str:
        last_exception: BaseException | None = None
        amount_of_retries = 0
        while not self._is_amount_of_retries_exceeded(amount=amount_of_retries):
            amount_of_retries += 1
            try:
                response: requests.Response = self.session.post(
                    url.as_string(),
                    data=data,
                    headers=self._json_headers(),
                    timeout=self.settings.timeout.total_seconds(),
                )
                data_received: str = response.content.decode()
                self._assert_status_code(status_code=response.status_code, sent=data, received=data_received)
                return data_received  # noqa: TRY300
            except requests.Timeout:
                last_exception = self._construct_timeout_exception(url, data, stopwatch.lap)
            except requests.exceptions.ConnectionError as error:
                raise CommunicationError(url=url.as_string(), request=data) from error
            except requests.exceptions.RequestException as error:
                last_exception = error
            self._sleep_for_retry()

        if last_exception is None:
            raise ValueError("Retry loop finished, but last_exception was not set")
        raise last_exception

    def teardown(self) -> None:
        self.session.close()
