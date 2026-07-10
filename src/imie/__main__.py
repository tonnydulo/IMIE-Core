import logging

from imie.config.settings import load_settings
from imie.engines.acceptance import AcceptanceAnalyst
from imie.engines.setup import SetupLifecycleEngine
from imie.engines.trend import TrendAnalyst
from imie.models import MarketSnapshot
from imie.engines.risk import RiskAnalyst
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

    trade_plan = RiskAnalyst(
    minimum_rr=2.0,
    target1_r=1.0,
    target2_r=2.0,
    ).analyze(
    context=context,
    freshness=freshness,
    trend_result=trend_result,
    lifecycle=lifecycle,
    acceptance=acceptance,
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

 # ============================================================
    # RISK ANALYST / TRADE PLAN
    # ============================================================
    print()
    print("Risk Analyst / Trade Plan")
    print(f"Decision     : {trade_plan.decision}")
    print(f"Valid        : {trade_plan.valid}")
    print(f"Actionable   : {trade_plan.actionable}")
    print(f"Quality      : {trade_plan.quality}")
    print(f"Confidence   : {trade_plan.confidence:.0f}")

    if trade_plan.entry is not None:
        print(f"Entry        : {trade_plan.entry:.2f}")
        print(f"Stop         : {trade_plan.stop:.2f}")
        print(f"Target 1     : {trade_plan.target1:.2f}")
        print(f"Target 2     : {trade_plan.target2:.2f}")
        print(f"Risk/Share   : {trade_plan.risk_per_share:.2f}")
        print(f"RR Target 1  : {trade_plan.rr1:.2f}")
        print(f"RR Target 2  : {trade_plan.rr2:.2f}")
    else:
        print("Entry        : n/a")
        print("Stop         : n/a")
        print("Target 1     : n/a")
        print("Target 2     : n/a")

    print(f"Narrative    : {trade_plan.narrative}")

    if trade_plan.reasons:
        print("Reasons      :")
        for item in trade_plan.reasons:
            print(f" - {item}")

    if trade_plan.warnings:
        print("Warnings     :")
        for item in trade_plan.warnings:
            print(f" - {item}")

    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
