from __future__ import annotations

from typing import Any

JsonT = dict[str, Any]
CommunicationResponseT = str | JsonT | list[JsonT]


class HelpyError(Exception):
    """Base class for all helpy Errors."""


class ParseError(HelpyError):
    """Raised if cannot parse given str, e.x. url, date, asset."""


class BlockWaitTimeoutError(HelpyError):
    """Raised if reached not expected block number."""

    def __init__(self, last_block_number: int, block_number: int, last_irreversible_block_number: int) -> None:
        """Creates exception.

        Arguments:
            last_block_number -- last fetched block number
            block_number -- block that was expected to be irreversible
            last_irreversible_block_number -- last fetched irreversible block number
        """
        super().__init__(
            f"Block with number `{last_block_number}` was just reached but expected `{block_number}` is still not"
            " irreversible.\n"
            f"Last irreversible block number is `{last_irreversible_block_number}`."
        )


class RequestError(HelpyError):
    """Raised if error field is in the response."""

    def __init__(self, send: str, error: str) -> None:
        """
        Initialize a RequestError.

        Parameters:
        - send (str): The request sent.
        - error (str): The error received in response.

        Returns:
        None
        """
        self.send = send
        self.error = error
        super().__init__(f"{send=} | {error=}")


class BatchRequestError(HelpyError):
    """Base class for batch related errors."""


class NothingToSendError(BatchRequestError):
    """Raised if there is nothing to send, example.

    with node.batch():
        pass
        # here on exit NothingToSendError will be raised
    """


class ResponseNotReadyError(BatchRequestError):
    """Raised on access to response when it's not ready.

    with node.batch() as x:
        resp = x.api.some_endpoint()
        assert resp.some_var == 1  # here ResponseNotReadyError will be raised
    """


class CommunicationError(HelpyError):
    """Base class for all communication related errors."""

    def __init__(
        self, url: str, request: str, response: CommunicationResponseT | None = None, *, message: str = ""
    ) -> None:
        """Contains required details.

        Args:
            url (str): where request has been send
            request (str): content of request
            response (CommunicationResponseT | None, optional): content of response. Defaults to None.
            message (str, optional): additional information about error. Defaults to "".
        """
        self.url = url
        self.request = request
        self.response = response
        message = message or self.__create_message()
        super().__init__(message)

    def get_response_error_messages(self) -> list[str]:
        """Obtains error message from response."""
        result = self.get_response()
        if result is None:
            return []

        if isinstance(result, dict):
            message = result.get("error", {}).get("message", None)
            return [str(message)] if message is not None else []

        messages = []
        for item in result:
            message = item.get("error", {}).get("message", None)
            if message is not None:
                messages.append(str(message))
        return messages

    def get_response(self) -> JsonT | list[JsonT] | None:  # noqa: D102
        return self.response if isinstance(self.response, dict | list) else None

    def _get_reply(self) -> str:
        if (result := self.get_response()) is not None:
            return f"response={result}"

        if self.response is not None:
            return f"response={self.response}"

        return "no response available"

    def __create_message(self) -> str:
        return (
            f"Problem occurred during communication with: url={self.url}, request={self.request}, {self._get_reply()}"
        )


class ExceededAmountOfRetriesError(CommunicationError):
    """Raised if exceeded amount of retries."""
