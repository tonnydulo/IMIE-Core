import logging

from imie.config.settings import load_settings
from imie.engines.facts import FactsEngine
from imie.models import MarketSnapshot
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

    snapshot = MarketSnapshot(
        symbol=symbol,
        timestamp=quote.timestamp,
        quote=quote,
        bars=bars,
        timeframe=timeframe,
    )

    facts_engine = FactsEngine()
    enriched_snapshot = facts_engine.enrich_snapshot(snapshot)

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version     : {IMIE_VERSION}")
    print(f"Environment : {settings.environment}")
    print(f"Provider    : {settings.default_provider}")
    print()
    print("OK Market Data Service Loaded")
    print(f"OK Provider Connected: {status.provider_name}")
    print("OK Market Snapshot Built")
    print("OK Facts Engine Loaded")
    print()
    print(f"Symbol       : {enriched_snapshot.symbol}")
    print(f"Timeframe    : {enriched_snapshot.timeframe}")
    print(f"Bars Loaded  : {len(enriched_snapshot.bars)}")
    print(f"Quote Last   : {enriched_snapshot.quote.last:.2f}")
    print(f"EMA9         : {enriched_snapshot.facts.ema9:.2f}")
    print(f"VWAP         : {enriched_snapshot.facts.vwap:.2f}")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
