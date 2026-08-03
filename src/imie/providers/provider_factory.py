from imie.providers.base_provider import MarketDataProvider
from imie.providers.mock_provider import MockProvider


class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> MarketDataProvider:
        normalized_name = provider_name.lower().strip()

        if normalized_name == "mock":
            return MockProvider()

        if normalized_name == "alpaca":
            from imie.providers.alpaca_provider import AlpacaProvider

            return AlpacaProvider()

        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )