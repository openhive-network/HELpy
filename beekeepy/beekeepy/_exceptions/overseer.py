from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from beekeepy.exceptions import BeekeepyError, CommunicationResponseT, Json, OverseerError

if TYPE_CHECKING:
    from beekeepy._communication.url import Url


class UnableToAcquireDatabaseLockError(OverseerError):
    def retry(self) -> bool:
        return True


class UnableToAcquireForkdbLockError(OverseerError):
    def retry(self) -> bool:
        return True


class NullResultError(OverseerError):
    def retry(self) -> bool:
        return True


class ApiNotFoundError(OverseerError):
    def retry(self) -> bool:
        return False

    @property
    def api(self) -> str:
        return self.message_raw.split(":")[-1].strip()


class JussiResponseError(OverseerError):
    def retry(self) -> bool:
        return True


class UnparsableResponseError(OverseerError):
    def retry(self) -> bool:
        return True


class DifferenceBetweenAmountOfRequestsAndResponsesError(OverseerError):
    def retry(self) -> bool:
        return True


class UnlockIsNotAccessibleError(OverseerError):
    def retry(self) -> bool:
        return False


class WalletIsAlreadyUnlockedError(OverseerError):
    def retry(self) -> bool:
        return False


class UnableToOpenWalletError(OverseerError):
    def retry(self) -> bool:
        return False


class OverseerInvalidPasswordError(OverseerError):
    def retry(self) -> bool:
        return False


class ErrorInResponseError(OverseerError):
    def __init__(  # noqa: PLR0913
        self,
        url: str | Url[Any],
        request: CommunicationResponseT | bytes,
        response: CommunicationResponseT | None = None,
        whole_response: CommunicationResponseT | None = None,
        *,
        message: str = "",
        request_id: int | None,
    ) -> None:
        super().__init__(
            url=url,
            request=request,
            response=response,
            message=message,
            request_id=request_id,
            whole_response=whole_response,
        )
        self.__error: str | None = None

    def retry(self) -> bool:
        return False

    @property
    def error(self) -> str:
        if self.__error is None:
            result = self._extract_error_messages(response=self.__get_suitable_response())
            self.__error = (result or [""])[0]
        return self.__error

    def __get_suitable_response(self) -> Json | str | None:
        if isinstance(self.response, list):
            if self.request_id is None:
                return None
            for item in self.response:
                if item.get("id", {}) == self.request_id:
                    return item
            return None
        return self.response


class GroupedErrorsError(BeekeepyError):
    def __init__(self, exceptions: Sequence[BaseException]) -> None:
        self.exceptions = list(exceptions)

    def get_exception_for(self, *, request_id: int) -> OverseerError | None:
        for exception in self.exceptions:
            if isinstance(exception, OverseerError) and exception.request_id == request_id:
                return exception
        return None
