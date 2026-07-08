from imie.models import MarketBar, ProviderStatus, Quote
from imie.providers.base_provider import MarketDataProvider
from imie.providers.provider_factory import ProviderFactory


class ProviderManager:
    def __init__(self, provider_name: str) -> None:
        self.provider: MarketDataProvider = ProviderFactory.create(provider_name)

    def connect(self) -> ProviderStatus:
        return self.provider.connect()

    def disconnect(self) -> ProviderStatus:
        return self.provider.disconnect()

    def get_quote(self, symbol: str) -> Quote:
        return self.provider.get_quote(symbol)

    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> list[MarketBar]:
        return self.provider.get_bars(symbol, timeframe, limit)
