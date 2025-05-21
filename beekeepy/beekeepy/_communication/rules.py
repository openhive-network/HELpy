from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, ClassVar, Final

from beekeepy._communication.abc.rules import OverseerRule
from beekeepy.exceptions import (
    ApiNotFoundError,
    DifferenceBetweenAmountOfRequestsAndResponsesError,
    ErrorInResponseError,
    Json,
    JussiResponseError,
    NullResultError,
    OverseerError,
    OverseerInvalidPasswordError,
    UnableToAcquireDatabaseLockError,
    UnableToAcquireForkdbLockError,
    UnableToOpenWalletError,
    UnknownDecisionPathError,
    UnlockIsNotAccessibleError,
    UnparsableResponseError,
    WalletIsAlreadyUnlockedError,
)

if TYPE_CHECKING:
    from beekeepy.exceptions import OverseerError


REGEX_FOR_PATH_WITH_CAPTURE_GROUP_ON_WALLET_NAME: Final[str] = r"\/(?:(?:[^\/]+\/)+)([^\/]+)\.wallet"


class UnableToAcquireDatabaseLock(OverseerRule):
    LOOKUP_MESSAGE: ClassVar[str] = "Unable to acquire database lock"

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if self.LOOKUP_MESSAGE in str(parsed_response):
            return [
                self._construct_exception(
                    error_cls=UnableToAcquireDatabaseLockError,
                    request_id=parsed_response.get("id"),
                    response=parsed_response,
                    message=f"Found `{self.LOOKUP_MESSAGE}` in response",
                    whole_response=whole_response,
                )
            ]
        return []


class UnableToAcquireForkdbLock(OverseerRule):
    LOOKUP_MESSAGE: ClassVar[str] = "Unable to acquire forkdb lock"

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if self.LOOKUP_MESSAGE in str(parsed_response):
            return [
                self._construct_exception(
                    error_cls=UnableToAcquireForkdbLockError,
                    message=f"Found `{self.LOOKUP_MESSAGE}` in response",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class NullResult(OverseerRule):
    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if parsed_response.get("result", {}) is None:
            request_id = int(parsed_response["id"])
            if self.is_excluded_request(request_id=request_id):
                return []

            return [
                self._construct_exception(
                    error_cls=NullResultError,
                    message="`result` field in response is null",
                    response=parsed_response,
                    request_id=request_id,
                    whole_response=whole_response,
                )
            ]

        return []

    def is_excluded_request(self, request_id: int) -> bool:
        request = self._get_matching_request(request_id=request_id)
        return request["method"] in [
            "wallet_bridge_api.get_account",
            "wallet_bridge_api.get_witness",
            "condenser_api.get_escrow",
        ]


class ApiNotFound(OverseerRule):
    _API_NOT_FOUND_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"Assert Exception:api_itr != data\._registered_apis\.end\(\): Could not find API (\w+_api)"
    )

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        search_result = self._API_NOT_FOUND_REGEX.search(str(parsed_response))
        if search_result is not None:
            return [
                self._construct_exception(
                    error_cls=ApiNotFoundError,
                    message=f"Requested api not found: {search_result.group(1)}",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class JussiResponse(OverseerRule):
    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if "jussi_request_id" in str(parsed_response):
            return [
                self._construct_exception(
                    error_cls=JussiResponseError,
                    message="Jussi responded instead of target service",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class UnparsableResponse(OverseerRule):
    def _check_non_json_response(self, parsed_response: Exception, response_raw: str) -> list[OverseerError]:
        if isinstance(parsed_response, json.JSONDecodeError):
            return [
                self._construct_exception(
                    error_cls=UnparsableResponseError,
                    message=(
                        "Received response is not parsable, " f"probably plaintext or invalid json: {response_raw}"
                    ),
                    response=parsed_response,
                    whole_response=response_raw,  # type: ignore[arg-type]
                    request_id=None,
                )
            ]
        return []

    def _check_single(
        self,
        parsed_response: Json,  # noqa: ARG002
        whole_response: Json | list[Json],  # noqa: ARG002
    ) -> list[OverseerError]:
        return []


class DifferenceBetweenAmountOfRequestsAndResponses(OverseerRule):
    def _check_batch(self, parsed_response: list[Json]) -> list[OverseerError]:
        def exception_factory(msg: str) -> OverseerError:
            return self._construct_exception(
                error_cls=DifferenceBetweenAmountOfRequestsAndResponsesError,
                message=msg,
                response=parsed_response,
                whole_response=parsed_response,
                request_id=None,
            )

        if not isinstance(self.request, list):
            return [exception_factory("Received list of responses (batch), while requesting singular response")]

        if (request_len := len(self.request)) != (response_len := len(parsed_response)):
            message_pattern: Final[str] = "Received {} responses than requested"

            if response_len == 0:
                return [exception_factory("Received no responses (empty array)")]

            if request_len < response_len:
                return [exception_factory(message_pattern % "more")]

            if request_len > response_len:
                return [exception_factory(message_pattern % "less")]

            raise UnknownDecisionPathError

        return []

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:  # noqa: ARG002
        return []


class ErrorInResponse(OverseerRule):
    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if (error := parsed_response.get("error")) is not None:
            return [
                self._construct_exception(
                    error_cls=ErrorInResponseError,
                    message=f"Error found in response: {error=}",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class UnlockIsNotAccessible(OverseerRule):
    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if "unlock is not accessible" in str(parsed_response):
            return [
                self._construct_exception(
                    error_cls=UnlockIsNotAccessibleError,
                    message="You tried to unlock wallet too fast",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class WalletIsAlreadyUnlocked(OverseerRule):
    _WALLET_IS_ALREADY_UNLOCKED_REGEXES: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"_itr->is_locked\(\): Wallet with name: '([\w-]+)' is already unlocked"),
        re.compile(r"_itr->is_locked\(\): Wallet is already unlocked: ([\w-]+)rethrow"),
    ]

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        for regex in self._WALLET_IS_ALREADY_UNLOCKED_REGEXES:
            if (match := regex.search(str(parsed_response))) is not None:
                return [
                    self._construct_exception(
                        error_cls=WalletIsAlreadyUnlockedError,
                        message=f"You tried to unlock already unlocked wallet: `{match.group(1)}`",
                        response=parsed_response,
                        request_id=parsed_response.get("id"),
                        whole_response=whole_response,
                    )
                ]
        return []


class UnableToOpenWallet(OverseerRule):
    _UNABLE_TO_OPEN_WALLET_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"_new_item->load_wallet_file\(\): "
        r"Unable to open file: " + REGEX_FOR_PATH_WITH_CAPTURE_GROUP_ON_WALLET_NAME + r"(?:rethrow)?"
    )

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if (match := self._UNABLE_TO_OPEN_WALLET_REGEX.search(str(parsed_response))) is not None:
            return [
                self._construct_exception(
                    error_cls=UnableToOpenWalletError,
                    message=f"No such wallet: {match.group(1)}",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []


class InvalidPassword(OverseerRule):
    _INVALID_PASSWORD_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"false: Invalid password for wallet: '" + REGEX_FOR_PATH_WITH_CAPTURE_GROUP_ON_WALLET_NAME + r"' (?:rethrow)?"
    )

    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        if (
            match := self._INVALID_PASSWORD_REGEX.search(parsed_response.get("error", {}).get("message", ""))
        ) is not None:
            return [
                self._construct_exception(
                    error_cls=OverseerInvalidPasswordError,
                    message=f"Invalid password for wallet: {match.group(1)}",
                    response=parsed_response,
                    request_id=parsed_response.get("id"),
                    whole_response=whole_response,
                )
            ]
        return []
