from __future__ import annotations

from helpy._interfaces.api.abc import AbstractAsyncApi
from schemas.apis import app_status_api  # noqa: TCH001


class AppStatusApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_app_status(self) -> app_status_api.GetAppStatus:
        raise NotImplementedError
