import logging

from imie.config.settings import load_settings
from imie.services import MarketDataService
from imie.utils.logging_utils import configure_logging
from imie.version import IMIE_NAME, IMIE_VERSION


def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger("imie")
    logger.info("Starting IMIE Core")

    market_data = MarketDataService(settings.default_provider)
    status = market_data.connect()
    quote = market_data.get_quote("NVDA")
    bars = market_data.get_bars("NVDA", "15m", limit=3)

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version     : {IMIE_VERSION}")
    print(f"Environment : {settings.environment}")
    print(f"Provider    : {settings.default_provider}")
    print("Status      : Initializing")
    print()
    print("OK Configuration Loaded")
    print("OK Logging Started")
    print("OK Market Data Service Loaded")
    print(f"OK Provider Connected: {status.provider_name}")
    print()
    print(f"Quote Symbol : {quote.symbol}")
    print(f"Quote Last   : {quote.last:.2f}")
    print(f"Quote Spread : {quote.spread:.2f}")
    print(f"Bars Loaded  : {len(bars)}")
    print(f"Bar Range    : {bars[0].range:.2f}")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
