from datetime import datetime

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

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
        raise NotImplementedError("Alpaca bars will be added in Sprint 4B.")
