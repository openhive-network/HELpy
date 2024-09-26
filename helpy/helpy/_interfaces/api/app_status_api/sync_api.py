from __future__ import annotations

from helpy._interfaces.api.abc import AbstractSyncApi
from schemas.apis import app_status_api  # noqa: TCH001


class AppStatusApi(AbstractSyncApi):
    api = AbstractSyncApi._endpoint

    @api
    def get_app_status(self) -> app_status_api.GetAppStatus:
        raise NotImplementedError
