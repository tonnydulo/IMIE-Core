from datetime import datetime, timedelta, timezone

from alpaca.common.enums import Sort
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from imie.config.settings import load_settings
from imie.models import MarketBar, ProviderStatus, Quote
from imie.providers.base_provider import MarketDataProvider


class AlpacaProvider(MarketDataProvider):
    provider_name = "alpaca"

    def __init__(self) -> None:
        self.settings = load_settings()
        self.client: StockHistoricalDataClient | None = None

    def connect(self) -> ProviderStatus:
        if not self.settings.alpaca_api_key or not self.settings.alpaca_secret_key:
            return ProviderStatus(
                provider_name=self.provider_name,
                connected=False,
                timestamp=datetime.now(timezone.utc),
                message="Missing Alpaca API credentials.",
            )

        self.client = StockHistoricalDataClient(
            self.settings.alpaca_api_key,
            self.settings.alpaca_secret_key,
        )

        return ProviderStatus(
            provider_name=self.provider_name,
            connected=True,
            timestamp=datetime.now(timezone.utc),
            message="Alpaca provider connected using the IEX market-data feed.",
        )

    def disconnect(self) -> ProviderStatus:
        self.client = None

        return ProviderStatus(
            provider_name=self.provider_name,
            connected=False,
            timestamp=datetime.now(timezone.utc),
            message="Alpaca provider disconnected.",
        )

    def get_quote(self, symbol: str) -> Quote:
        client = self._require_client()

        request = StockLatestQuoteRequest(
            symbol_or_symbols=symbol,
            feed=DataFeed.IEX,
        )
        response = client.get_stock_latest_quote(request)
        alpaca_quote = response[symbol]

        bid = float(alpaca_quote.bid_price)
        ask = float(alpaca_quote.ask_price)

        return Quote(
            symbol=symbol,
            timestamp=alpaca_quote.timestamp,
            bid=bid,
            ask=ask,
            last=(bid + ask) / 2.0,
            volume=0,
            provider=self.provider_name,
        )

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[MarketBar]:
        if limit <= 0:
            raise ValueError("Bar limit must be greater than zero.")

        client = self._require_client()
        alpaca_timeframe = self._convert_timeframe(timeframe)
        now_utc = datetime.now(timezone.utc)

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=alpaca_timeframe,
            start=now_utc - timedelta(days=30),
            end=now_utc,
            limit=limit,
            sort=Sort.DESC,
            feed=DataFeed.IEX,
        )

        response = client.get_stock_bars(request)
        alpaca_bars = list(response[symbol])

        if not alpaca_bars:
            raise RuntimeError(
                f"Alpaca returned no {timeframe} IEX bars for {symbol}."
            )

        # The descending request returns newest bars first.
        # IMIE indicators require chronological order.
        alpaca_bars.reverse()

        return [
            MarketBar(
                symbol=symbol,
                timestamp=bar.timestamp,
                open=float(bar.open),
                high=float(bar.high),
                low=float(bar.low),
                close=float(bar.close),
                volume=int(bar.volume),
                timeframe=timeframe,
                provider=self.provider_name,
            )
            for bar in alpaca_bars
        ]

    def _require_client(self) -> StockHistoricalDataClient:
        if self.client is None:
            status = self.connect()

            if not status.connected or self.client is None:
                raise RuntimeError(status.message)

        return self.client

    def _convert_timeframe(self, timeframe: str) -> TimeFrame:
        normalized = timeframe.lower().strip()

        supported = {
            "1m": TimeFrame(1, TimeFrameUnit.Minute),
            "2m": TimeFrame(2, TimeFrameUnit.Minute),
            "5m": TimeFrame(5, TimeFrameUnit.Minute),
            "15m": TimeFrame(15, TimeFrameUnit.Minute),
            "1d": TimeFrame(1, TimeFrameUnit.Day),
        }

        if normalized not in supported:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        return supported[normalized]
