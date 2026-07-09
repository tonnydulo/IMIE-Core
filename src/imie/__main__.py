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

    symbol = "NVDA"
    timeframe = "2m"

    market_data = MarketDataService(settings.default_provider)
    status = market_data.connect()
    quote = market_data.get_quote(symbol)
    bars = market_data.get_bars(symbol, timeframe, limit=500)

    latest_bar = bars[-1]

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
    print(f"Quote Bid    : {quote.bid:.2f}")
    print(f"Quote Ask    : {quote.ask:.2f}")
    print(f"Quote Last   : {quote.last:.2f}")
    print(f"Quote Spread : {quote.spread:.2f}")
    print()
    print(f"Bars Symbol  : {symbol}")
    print(f"Bars TF      : {timeframe}")
    print(f"Bars Loaded  : {len(bars)}")
    print(f"Latest Close : {latest_bar.close:.2f}")
    print(f"Latest Range : {latest_bar.range:.2f}")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
