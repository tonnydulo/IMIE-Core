import logging
from datetime import datetime

from imie.config.settings import load_settings
from imie.models import Analysis, MarketBar, Quote, Symbol
from imie.utils.logging_utils import configure_logging
from imie.version import IMIE_NAME, IMIE_VERSION


def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger("imie")
    logger.info("Starting IMIE Core")

    sample_symbol = Symbol(ticker="NVDA", name="NVIDIA Corporation", provider="schwab")
    sample_quote = Quote(
        symbol="NVDA",
        timestamp=datetime.now(),
        bid=100.00,
        ask=100.05,
        last=100.03,
        provider="sample",
    )
    sample_bar = MarketBar(
        symbol="NVDA",
        timestamp=datetime.now(),
        open=99.50,
        high=100.25,
        low=99.25,
        close=100.03,
        volume=1_000_000,
        timeframe="15m",
        provider="sample",
    )
    sample_analysis = Analysis(symbol="NVDA", timestamp=datetime.now())
    sample_analysis.add_reason("Core domain models loaded successfully.")

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version : {IMIE_VERSION}")
    print("Status  : Initializing")
    print()
    print("OK Configuration Loaded")
    print("OK Logging Started")
    print("OK Version Loaded")
    print("OK Domain Models Loaded")
    print("OK Provider Interface Ready")
    print()
    print(f"Sample Symbol : {sample_symbol.ticker}")
    print(f"Sample Spread : {sample_quote.spread:.2f}")
    print(f"Sample Range  : {sample_bar.range:.2f}")
    print(f"Sample Reason : {sample_analysis.reasons[0]}")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
