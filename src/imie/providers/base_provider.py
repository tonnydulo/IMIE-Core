from abc import ABC, abstractmethod

from imie.models import MarketBar, ProviderStatus, Quote


class MarketDataProvider(ABC):
    provider_name: str

    @abstractmethod
    def connect(self) -> ProviderStatus:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> ProviderStatus:
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> list[MarketBar]:
        raise NotImplementedError
