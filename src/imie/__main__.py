import logging

from imie.config.settings import load_settings
from imie.engines.setup import SetupLifecycleEngine
from imie.engines.trend import TrendAnalyst
from imie.models import MarketSnapshot
from imie.services import ContextBuilder, MarketDataService
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

    context_builder = ContextBuilder(atr_tolerance=0.25)
    context = context_builder.build(snapshot)

    trend_analyst = TrendAnalyst()
    trend_result = trend_analyst.analyze(context)

    lifecycle_engine = SetupLifecycleEngine()
    lifecycle = lifecycle_engine.evaluate_pullback_to_core(context, trend_result)

    measurements = context.measurements
    observations = context.observations

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version     : {IMIE_VERSION}")
    print(f"Environment : {settings.environment}")
    print(f"Provider    : {settings.default_provider}")
    print()
    print("OK Market Data Service Loaded")
    print(f"OK Provider Connected: {status.provider_name}")
    print("OK TradingContext Built")
    print("OK TrendAnalyst Loaded")
    print("OK Setup Lifecycle Engine Loaded")
    print()
    print(f"Symbol       : {context.snapshot.symbol}")
    print(f"Timeframe    : {context.snapshot.timeframe}")
    print(f"Bars Loaded  : {len(context.snapshot.bars)}")
    print(f"Quote Last   : {measurements.price:.2f}")
    print(f"EMA9         : {measurements.ema9:.2f}" if measurements.ema9 else "EMA9         : n/a")
    print(f"Prev EMA9    : {measurements.previous_ema9:.2f}" if measurements.previous_ema9 else "Prev EMA9    : n/a")
    print(f"EMA9 Slope   : {measurements.ema9_slope:.4f}" if measurements.ema9_slope else "EMA9 Slope   : n/a")
    print(f"VWAP         : {measurements.vwap:.2f}" if measurements.vwap else "VWAP         : n/a")
    print(f"ATR14        : {measurements.atr14:.2f}" if measurements.atr14 else "ATR14        : n/a")
    print()
    print("Observations")
    print(f"Above EMA9   : {observations.price_above_ema9}")
    print(f"Above VWAP   : {observations.price_above_vwap}")
    print(f"EMA9 Rising  : {observations.ema9_rising}")
    print(f"At Core      : {observations.within_core_zone}")
    print(f"Approaching  : {observations.approaching_core}")
    print()
    print("Trend Analyst")
    print(f"Opinion      : {trend_result.opinion}")
    print(f"Confidence   : {trend_result.confidence:.0f}")
    print()
    print("Setup Lifecycle")
    print(f"State        : {lifecycle.state}")
    print(f"Direction    : {lifecycle.direction}")
    print(f"Confidence   : {lifecycle.confidence:.0f}")
    print(f"ATR Distance : {lifecycle.atr_distance:.2f}" if lifecycle.atr_distance is not None else "ATR Distance : n/a")
    print(f"Action       : {lifecycle.action}")
    print(f"Reason       : {lifecycle.reason}")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
