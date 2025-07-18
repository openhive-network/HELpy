from __future__ import annotations

from beekeepy._apis.abc.api import AbstractSyncApi
from schemas.apis import app_status_api  # noqa: TCH001


class AppStatusApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def get_app_status(self) -> app_status_api.GetAppStatus:
        raise NotImplementedError
