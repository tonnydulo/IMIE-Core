from typing import Any

__all__ = [
    "AlpacaProvider",
    "MarketDataProvider",
    "MockProvider",
    "ProviderFactory",
    "ProviderManager",
]


def __getattr__(name: str) -> Any:
    if name == "AlpacaProvider":
        from imie.providers.alpaca_provider import AlpacaProvider

        return AlpacaProvider

    if name == "MarketDataProvider":
        from imie.providers.base_provider import MarketDataProvider

        return MarketDataProvider

    if name == "MockProvider":
        from imie.providers.mock_provider import MockProvider

        return MockProvider

    if name == "ProviderFactory":
        from imie.providers.provider_factory import ProviderFactory

        return ProviderFactory

    if name == "ProviderManager":
        from imie.providers.provider_manager import ProviderManager

        return ProviderManager

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )