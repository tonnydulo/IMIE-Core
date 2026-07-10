import logging

from imie.config.settings import load_settings
from imie.engines.acceptance import AcceptanceAnalyst
from imie.engines.setup import SetupLifecycleEngine
from imie.engines.trend import TrendAnalyst
from imie.models import MarketSnapshot
from imie.services import (
    ContextBuilder,
    DataFreshnessGuard,
    MarketDataService,
)
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

    freshness = DataFreshnessGuard().evaluate(snapshot)

    context = ContextBuilder(
        atr_tolerance=0.25,
    ).build(snapshot)

    trend_result = TrendAnalyst().analyze(context)

    lifecycle_engine = SetupLifecycleEngine()
    lifecycle = lifecycle_engine.evaluate_pullback_to_core(
        context,
        trend_result,
    )

    acceptance = AcceptanceAnalyst().analyze(
        context,
        lifecycle,
    )

    if acceptance.accepted:
        lifecycle = lifecycle_engine.evaluate_pullback_to_core(
            context,
            trend_result,
            acceptance_confirmed=True,
        )

    measurements = context.measurements

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version     : {IMIE_VERSION}")
    print(f"Environment : {settings.environment}")
    print(f"Provider    : {settings.default_provider}")
    print()
    print("OK Market Data Service Loaded")
    print(f"OK Provider Connected: {status.provider_name}")
    print("OK Data Freshness Guard Loaded")
    print("OK TradingContext Built")
    print("OK TrendAnalyst Loaded")
    print("OK Setup Lifecycle Engine Loaded")
    print("OK AcceptanceAnalyst Loaded")
    print()
    print("Data Freshness")
    print(f"Status       : {freshness.status}")
    print(f"Actionable   : {freshness.actionable}")
    print(f"Quote Age    : {freshness.quote_age_seconds:.1f} sec")
    print(f"Bar Age      : {freshness.bar_age_seconds:.1f} sec")
    print(f"Quote/Bar Gap: {freshness.quote_bar_gap_seconds:.1f} sec")
    print()
    print(f"Symbol       : {context.snapshot.symbol}")
    print(f"Timeframe    : {context.snapshot.timeframe}")
    print(f"Quote Last   : {measurements.price:.2f}")
    print(f"EMA9         : {measurements.ema9:.2f}" if measurements.ema9 is not None else "EMA9         : n/a")
    print(f"VWAP         : {measurements.vwap:.2f}" if measurements.vwap is not None else "VWAP         : n/a")
    print(f"ATR14        : {measurements.atr14:.2f}" if measurements.atr14 is not None else "ATR14        : n/a")
    print()
    print("Trend Analyst")
    print(f"Opinion      : {trend_result.opinion}")
    print(f"Confidence   : {trend_result.confidence:.0f}")
    print()
    print("Acceptance Analyst")
    print(f"Accepted     : {acceptance.accepted}")
    print(f"Level        : {acceptance.level}")
    print(f"Score        : {acceptance.score}")
    print(f"Trigger Price: {acceptance.trigger_price:.2f}" if acceptance.trigger_price is not None else "Trigger Price: n/a")
    print(f"Prior Level  : {acceptance.previous_level:.2f}" if acceptance.previous_level is not None else "Prior Level  : n/a")
    print(f"Reason       : {acceptance.reason}")

    if acceptance.evidence:
        print("Evidence     :")
        for item in acceptance.evidence:
            print(f" - {item}")

    if acceptance.warnings:
        print("Warnings     :")
        for item in acceptance.warnings:
            print(f" - {item}")

    print()
    print("Setup Lifecycle")
    print(f"State        : {lifecycle.state}")
    print(f"Direction    : {lifecycle.direction}")
    print(f"ATR Distance : {lifecycle.atr_distance:.2f}" if lifecycle.atr_distance is not None else "ATR Distance : n/a")

    if freshness.actionable:
        print(f"Action       : {lifecycle.action}")
        print(f"Reason       : {lifecycle.reason}")
    else:
        print("Action       : DATA NOT ACTIONABLE")
        print(f"Reason       : {freshness.reason}")

    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
