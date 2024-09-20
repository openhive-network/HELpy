from __future__ import annotations

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import reputation_api  # noqa: TCH001


class ReputationApi(AbstractAsyncApi):
    @AbstractAsyncApi._endpoint
    async def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputations:
        raise NotImplementedError
