from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Iterator, Sequence

if TYPE_CHECKING:
    from beekeepy._communication.url import HttpUrl
    from beekeepy.exceptions import Json, OverseerError


class ContinueMode(IntEnum):
    BREAK = 0
    CONTINUE = 1
    INF = 2


@dataclass(kw_only=True)
class RulesClassifier:
    preliminary: Sequence[type[OverseerRule]]
    """Checks if content is parsable and is in valid state."""

    infinitely_repeatable: Sequence[type[OverseerRule]]
    """Checks if response should be acquired until approval."""

    finitely_repeatable: Sequence[type[OverseerRule]]
    """Checks if response is ok just settings.max_retries, after this rethrows."""

    def instantiate(self, url: HttpUrl, request: Json | list[Json] | None) -> Rules:
        return Rules(
            preliminary=[rule_cls(url=url, request=request) for rule_cls in self.preliminary],
            infinitely_repeatable=[rule_cls(url=url, request=request) for rule_cls in self.infinitely_repeatable],
            finitely_repeatable=[rule_cls(url=url, request=request) for rule_cls in self.finitely_repeatable],
        )


@dataclass(kw_only=True)
class RulesExceptions:
    preliminary: Sequence[type[OverseerError]]
    infinitely_repeatable: Sequence[type[OverseerError]]
    finitely_repeatable: Sequence[type[OverseerError]]


@dataclass(kw_only=True, frozen=True)
class Rules:
    preliminary: Sequence[OverseerRule]
    """If rules in this category detect error, retries won't be attempted."""

    infinitely_repeatable: Sequence[OverseerRule]
    """If rules in this category detect error, retries will be attempted indefinitely."""

    finitely_repeatable: Sequence[OverseerRule]
    """If rules in this category detect error, retries will be attempted up to settings.max_retries times."""

    def resolved_rules(self) -> Iterator[tuple[OverseerRule, ContinueMode]]:
        """Yields all rules in proper order with their associated ContinueMode."""
        yield from  (
            *((rule, ContinueMode.INF) for rule in self.infinitely_repeatable),
            *((rule, ContinueMode.BREAK) for rule in self.preliminary),
            *((rule, ContinueMode.CONTINUE) for rule in self.finitely_repeatable),
        )

    def grouped_exceptions(self) -> RulesExceptions:
        return RulesExceptions(
            preliminary=[rule.expected_exception() for rule in self.preliminary],
            infinitely_repeatable=[rule.expected_exception() for rule in self.infinitely_repeatable],
            finitely_repeatable=[rule.expected_exception() for rule in self.finitely_repeatable],
        )


class OverseerRule(ABC):
    def __init__(self, url: HttpUrl, request: Json | list[Json] | None) -> None:
        self.url = url
        self.request = request or {}  # if None, then this is REST request

    def check(self, response: Json | list[Json] | Exception, response_raw: str) -> list[OverseerError]:
        """Call to verify response."""
        if isinstance(response, list):
            return self._check_batch(parsed_response=response)
        if isinstance(response, dict):
            return self._check_single(parsed_response=response, whole_response=response)
        return self._check_non_json_response(parsed_response=response, response_raw=response_raw)

    def _check_batch(self, parsed_response: list[Json]) -> list[OverseerError]:
        """Overload this method to verify response as a whole in case of array (batch).

        Note: by default in case of array response calls `_check_single` for each element.
        """
        result: list[OverseerError] = []
        for response in parsed_response:
            result.extend(self._check_single(parsed_response=response, whole_response=parsed_response))
        return result

    def _check_non_json_response(self, parsed_response: Exception, response_raw: str) -> list[OverseerError]:  # noqa: ARG002
        """Overload this method to verify non-json response."""
        return []

    @abstractmethod
    def _check_single(self, parsed_response: Json, whole_response: Json | list[Json]) -> list[OverseerError]:
        """Overload this method to verify response in case of singular response."""

    def _get_matching_request(self, request_id: int) -> Json:
        """Searches for request of given id in case of array (batch) result. In case of singular request, returns it."""
        if isinstance(self.request, list):
            for req in self.request:
                assert isinstance(req, dict), "All items in batch request has to be json objects"
                if req.get("id", {}) == request_id:
                    return req
        assert isinstance(self.request, dict), f"self.request is not a dict, nor list, but is `{type(self.request)}`"
        return self.request

    @classmethod
    @abstractmethod
    def expected_exception(cls) -> type[OverseerError]:
        """Overload this method to specify which exception should be raised in case of detection."""

    def _construct_exception(
        self,
        response: Json | list[Json] | Exception,
        whole_response: Json | list[Json],
        request_id: int | None,
        message: str = "",
    ) -> OverseerError:
        return self.expected_exception()(
            url=self.url,
            request=self.request,
            request_id=request_id,
            response=(str(response) if isinstance(response, Exception) else response),
            whole_response=whole_response,
            message=message,
        )
