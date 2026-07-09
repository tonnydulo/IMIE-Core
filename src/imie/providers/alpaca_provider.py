from datetime import datetime, timedelta

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
                timestamp=datetime.now(),
                message="Missing Alpaca API credentials.",
            )

        self.client = StockHistoricalDataClient(
            self.settings.alpaca_api_key,
            self.settings.alpaca_secret_key,
        )

        return ProviderStatus(
            provider_name=self.provider_name,
            connected=True,
            timestamp=datetime.now(),
            message="Alpaca provider connected.",
        )

    def disconnect(self) -> ProviderStatus:
        self.client = None
        return ProviderStatus(
            provider_name=self.provider_name,
            connected=False,
            timestamp=datetime.now(),
            message="Alpaca provider disconnected.",
        )

    def get_quote(self, symbol: str) -> Quote:
        if self.client is None:
            self.connect()

        if self.client is None:
            raise RuntimeError("Alpaca client is not connected.")

        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        response = self.client.get_stock_latest_quote(request)
        alpaca_quote = response[symbol]

        bid = float(alpaca_quote.bid_price)
        ask = float(alpaca_quote.ask_price)

        return Quote(
            symbol=symbol,
            timestamp=alpaca_quote.timestamp,
            bid=bid,
            ask=ask,
            last=(bid + ask) / 2,
            volume=0,
            provider=self.provider_name,
        )

    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> list[MarketBar]:
        if self.client is None:
            self.connect()

        if self.client is None:
            raise RuntimeError("Alpaca client is not connected.")

        alpaca_timeframe = self._convert_timeframe(timeframe)

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=alpaca_timeframe,
            start=datetime.now() - timedelta(days=10),
            limit=limit,
        )

        response = self.client.get_stock_bars(request)
        bars = response[symbol]

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
            for bar in bars
        ]

    def _convert_timeframe(self, timeframe: str) -> TimeFrame:
        normalized = timeframe.lower().strip()

        if normalized == "1m":
            return TimeFrame(1, TimeFrameUnit.Minute)

        if normalized == "2m":
            return TimeFrame(2, TimeFrameUnit.Minute)

        if normalized == "5m":
            return TimeFrame(5, TimeFrameUnit.Minute)

        if normalized == "15m":
            return TimeFrame(15, TimeFrameUnit.Minute)

        if normalized == "1d":
            return TimeFrame(1, TimeFrameUnit.Day)

        raise ValueError(f"Unsupported timeframe: {timeframe}")
