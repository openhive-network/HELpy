from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from helpy._interfaces.api.abc import AbstractAsyncApi
from helpy._interfaces.asset.asset import Hf26Asset  # noqa: TCH001
from schemas.apis import market_history_api  # noqa: TCH001


class MarketHistoryApi(AbstractAsyncApi):
    api = AbstractAsyncApi._endpoint

    @api
    async def get_ticker(self) -> market_history_api.GetTicker[Hf26Asset.HiveT, Hf26Asset.HbdT]:
        raise NotImplementedError

    @api
    async def get_volume(self) -> market_history_api.GetVolume[Hf26Asset.HiveT, Hf26Asset.HbdT]:
        raise NotImplementedError

    @api
    async def get_order_book(
        self, *, limit: int = 500
    ) -> market_history_api.GetOrderBook[Hf26Asset.HiveT, Hf26Asset.HbdT, Hf26Asset.VestsT]:
        raise NotImplementedError

    @api
    async def get_trade_history(
        self, *, start: datetime, end: datetime, limit: int = 1000
    ) -> market_history_api.GetTradeHistory:
        raise NotImplementedError

    @api
    async def get_recent_trades(self, *, limit: int = 1000) -> market_history_api.GetRecentTrades:
        raise NotImplementedError

    @api
    async def get_market_history(
        self, *, start: datetime, end: datetime, bucket_seconds: int = 0
    ) -> market_history_api.GetMarketHistory:
        raise NotImplementedError

    @api
    async def get_market_history_buckets(self) -> market_history_api.GetMarketHistoryBuckets:
        raise NotImplementedError
