import logging

from imie.config.settings import load_settings
from imie.providers import ProviderManager
from imie.utils.logging_utils import configure_logging
from imie.version import IMIE_NAME, IMIE_VERSION


def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger("imie")
    logger.info("Starting IMIE Core")

    provider_manager = ProviderManager("mock")
    status = provider_manager.connect()
    quote = provider_manager.get_quote("NVDA")
    bars = provider_manager.get_bars("NVDA", "15m", limit=3)

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version : {IMIE_VERSION}")
    print("Status  : Initializing")
    print()
    print("OK Configuration Loaded")
    print("OK Logging Started")
    print("OK Provider Framework Loaded")
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
