from datetime import datetime, timezone

from imie.models import (
    MarketBar,
    ProviderStatus,
    Quote,
)
from imie.providers.base_provider import (
    MarketDataProvider,
)


class MockProvider(MarketDataProvider):
    provider_name = "mock"

    def connect(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.provider_name,
            connected=True,
            timestamp=datetime.now(
                timezone.utc
            ),
            message="Mock provider connected.",
        )

    def disconnect(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.provider_name,
            connected=False,
            timestamp=datetime.now(
                timezone.utc
            ),
            message="Mock provider disconnected.",
        )

    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        return Quote(
            symbol=symbol,
            timestamp=datetime.now(
                timezone.utc
            ),
            bid=100.00,
            ask=100.05,
            last=100.03,
            volume=1_000_000,
            provider=self.provider_name,
        )

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[MarketBar]:
        return [
            MarketBar(
                symbol=symbol,
                timestamp=datetime.now(
                    timezone.utc
                ),
                open=99.50,
                high=100.25,
                low=99.25,
                close=100.03,
                volume=1_000_000,
                timeframe=timeframe,
                provider=self.provider_name,
            )
            for _ in range(limit)
        ]