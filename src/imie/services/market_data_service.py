from imie.models import MarketBar, ProviderStatus, Quote
from imie.providers import ProviderManager


class MarketDataService:
    def __init__(self, provider_name: str) -> None:
        self.provider_manager = ProviderManager(provider_name)

    def connect(self) -> ProviderStatus:
        return self.provider_manager.connect()

    def disconnect(self) -> ProviderStatus:
        return self.provider_manager.disconnect()

    def get_quote(self, symbol: str) -> Quote:
        return self.provider_manager.get_quote(symbol)

    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> list[MarketBar]:
        return self.provider_manager.get_bars(symbol, timeframe, limit)
