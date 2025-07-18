from __future__ import annotations

from beekeepy._apis.abc.api import AbstractAsyncApi
from schemas.apis import app_status_api  # noqa: TCH001


class AppStatusApi(AbstractAsyncApi):
    api = AbstractAsyncApi.endpoint_jsonrpc

    @api
    async def get_app_status(self) -> app_status_api.GetAppStatus:
        raise NotImplementedError
