from __future__ import annotations

from helpy._handles.abc.api import AbstractSyncApi
from schemas.apis import reputation_api  # noqa: TCH001


class ReputationApi(AbstractSyncApi):
    @AbstractSyncApi._endpoint
    def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputations:
        raise NotImplementedError
