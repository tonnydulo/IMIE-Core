import logging
from dataclasses import replace

from imie.config.settings import load_settings
from imie.directors import DecisionDirector
from imie.engines.acceptance import AcceptanceAnalyst
from imie.engines.risk import RiskAnalyst
from imie.engines.setup import SetupLifecycleEngine
from imie.engines.trend import TrendAnalyst
from imie.models import (
    AcceptanceResult,
    AnalystRegistry,
    MarketSnapshot,
    SetupLifecycle,
    TradePlan,
)
from imie.services import (
    ContextBuilder,
    DataFreshnessGuard,
    MarketDataService,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_TREND,
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

    # ============================================================
    # MARKET DATA
    # ============================================================
    market_data = MarketDataService(settings.default_provider)

    status = market_data.connect()
    quote = market_data.get_quote(symbol)
    bars = market_data.get_bars(
        symbol,
        timeframe,
        limit=500,
    )

    snapshot = MarketSnapshot(
        symbol=symbol,
        timestamp=quote.timestamp,
        quote=quote,
        bars=bars,
        timeframe=timeframe,
    )

    # ============================================================
    # DATA FRESHNESS
    # ============================================================
    freshness = DataFreshnessGuard().evaluate(snapshot)

    # ============================================================
    # TRADING CONTEXT
    # ============================================================
    context = ContextBuilder(
        atr_tolerance=0.25,
    ).build(snapshot)

    # ============================================================
    # TREND ANALYST
    # ============================================================
    trend_result = TrendAnalyst().analyze(context)

    trend_result = replace(
        trend_result,
        analyst_id=ANALYST_TREND,
    )

    # ============================================================
    # SETUP LIFECYCLE — INITIAL EVALUATION
    # ============================================================
    lifecycle_engine = SetupLifecycleEngine()

    initial_lifecycle = lifecycle_engine.evaluate_pullback_to_core(
        context,
        trend_result,
    )

    # ============================================================
    # ACCEPTANCE ANALYST
    # ============================================================
    acceptance_analyst = AcceptanceAnalyst()

    acceptance_result = acceptance_analyst.analyze_result(
        context,
        initial_lifecycle,
    )

    acceptance_result = replace(
        acceptance_result,
        analyst_id=ANALYST_ACCEPTANCE,
    )

    acceptance = acceptance_result.payload

    if not isinstance(acceptance, AcceptanceResult):
        raise TypeError(
            "AcceptanceAnalyst did not produce an AcceptanceResult payload."
        )

    # ============================================================
    # SETUP LIFECYCLE — FINAL EVALUATION
    # ============================================================
    setup_result = lifecycle_engine.analyze(
        context,
        trend_result,
        acceptance_confirmed=acceptance.accepted,
    )

    setup_result = replace(
        setup_result,
        analyst_id=ANALYST_SETUP,
    )

    lifecycle = setup_result.payload

    if not isinstance(lifecycle, SetupLifecycle):
        raise TypeError(
            "SetupLifecycleEngine did not produce a SetupLifecycle payload."
        )

    # ============================================================
    # RISK ANALYST / TRADE PLAN
    # ============================================================
    risk_analyst = RiskAnalyst(
        minimum_rr=2.0,
        target1_r=1.0,
        target2_r=2.0,
    )

    risk_result = risk_analyst.analyze_result(
        context=context,
        freshness=freshness,
        trend_result=trend_result,
        lifecycle=lifecycle,
        acceptance=acceptance,
    )

    risk_result = replace(
        risk_result,
        analyst_id=ANALYST_RISK,
    )

    trade_plan = risk_result.payload

    if not isinstance(trade_plan, TradePlan):
        raise TypeError(
            "RiskAnalyst did not produce a TradePlan payload."
        )

    # ============================================================
    # ANALYST REGISTRY
    # ============================================================
    registry = AnalystRegistry()

    registry.register(trend_result)
    registry.register(setup_result)
    registry.register(acceptance_result)
    registry.register(risk_result)

    # ============================================================
    # DECISION DIRECTOR
    # ============================================================
    decision_result = DecisionDirector().evaluate(
    context=context,
    freshness=freshness,
    registry=registry,
)

    measurements = context.measurements

    # ============================================================
    # SYSTEM HEADER
    # ============================================================
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
    print("OK RiskAnalyst Loaded")
    print("OK AnalystRegistry Loaded")
    print("OK DecisionDirector Loaded")

    # ============================================================
    # DATA FRESHNESS OUTPUT
    # ============================================================
    print()
    print("Data Freshness")
    print(f"Status       : {freshness.status}")
    print(f"Actionable   : {freshness.actionable}")
    print(f"Quote Age    : {freshness.quote_age_seconds:.1f} sec")
    print(f"Bar Age      : {freshness.bar_age_seconds:.1f} sec")
    print(
        f"Quote/Bar Gap: "
        f"{freshness.quote_bar_gap_seconds:.1f} sec"
    )

    # ============================================================
    # MARKET MEASUREMENTS OUTPUT
    # ============================================================
    print()
    print(f"Symbol       : {context.snapshot.symbol}")
    print(f"Timeframe    : {context.snapshot.timeframe}")
    print(f"Quote Last   : {measurements.price:.2f}")

    if measurements.ema9 is not None:
        print(f"EMA9         : {measurements.ema9:.2f}")
    else:
        print("EMA9         : n/a")

    if measurements.vwap is not None:
        print(f"VWAP         : {measurements.vwap:.2f}")
    else:
        print("VWAP         : n/a")

    if measurements.atr14 is not None:
        print(f"ATR14        : {measurements.atr14:.2f}")
    else:
        print("ATR14        : n/a")

    # ============================================================
    # TREND ANALYST OUTPUT
    # ============================================================
    print()
    print("Trend Analyst")
    print(f"Opinion      : {trend_result.opinion}")
    print(f"Confidence   : {trend_result.confidence:.0f}")

    if trend_result.evidence:
        print("Evidence     :")

        for item in trend_result.evidence:
            print(f" - {item}")

    if trend_result.warnings:
        print("Warnings     :")

        for item in trend_result.warnings:
            print(f" - {item}")

    # ============================================================
    # ACCEPTANCE ANALYST OUTPUT
    # ============================================================
    print()
    print("Acceptance Analyst")
    print(f"Accepted     : {acceptance.accepted}")
    print(f"Level        : {acceptance.level}")
    print(f"Score        : {acceptance.score}")

    if acceptance.trigger_price is not None:
        print(f"Trigger Price: {acceptance.trigger_price:.2f}")
    else:
        print("Trigger Price: n/a")

    if acceptance.previous_level is not None:
        print(f"Prior Level  : {acceptance.previous_level:.2f}")
    else:
        print("Prior Level  : n/a")

    print(f"Reason       : {acceptance.reason}")

    if acceptance.evidence:
        print("Evidence     :")

        for item in acceptance.evidence:
            print(f" - {item}")

    if acceptance.warnings:
        print("Warnings     :")

        for item in acceptance.warnings:
            print(f" - {item}")

    # ============================================================
    # SETUP LIFECYCLE OUTPUT
    # ============================================================
    print()
    print("Setup Lifecycle")
    print(f"State        : {lifecycle.state}")
    print(f"Direction    : {lifecycle.direction}")

    if lifecycle.atr_distance is not None:
        print(f"ATR Distance : {lifecycle.atr_distance:.2f}")
    else:
        print("ATR Distance : n/a")

    if freshness.actionable:
        print(f"Action       : {lifecycle.action}")
        print(f"Reason       : {lifecycle.reason}")
    else:
        print("Action       : DATA NOT ACTIONABLE")
        print(f"Reason       : {freshness.reason}")

    # ============================================================
    # RISK ANALYST / TRADE PLAN OUTPUT
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

        if trade_plan.stop is not None:
            print(f"Stop         : {trade_plan.stop:.2f}")
        else:
            print("Stop         : n/a")

        if trade_plan.target1 is not None:
            print(f"Target 1     : {trade_plan.target1:.2f}")
        else:
            print("Target 1     : n/a")

        if trade_plan.target2 is not None:
            print(f"Target 2     : {trade_plan.target2:.2f}")
        else:
            print("Target 2     : n/a")

        if trade_plan.risk_per_share is not None:
            print(
                f"Risk/Share   : "
                f"{trade_plan.risk_per_share:.2f}"
            )

        if trade_plan.rr1 is not None:
            print(f"RR Target 1  : {trade_plan.rr1:.2f}")

        if trade_plan.rr2 is not None:
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

    # ============================================================
    # DECISION DIRECTOR OUTPUT
    # ============================================================
    print()
    print("=" * 60)
    print("Decision Director")
    print("=" * 60)
    print(f"Decision     : {decision_result.decision.value}")
    print(f"Actionable   : {decision_result.actionable}")
    print(f"Confidence   : {decision_result.confidence:.0f}")
    print(
        f"Recommendation: "
        f"{decision_result.recommendation}"
    )

    print()
    print("Analyst Summary")

    if decision_result.analyst_summary:
        for analyst_id, summary in (
            decision_result.analyst_summary.items()
        ):
            opinion = summary.get("opinion", "")
            confidence = float(
                summary.get("confidence", 0.0)
            )
            enabled = bool(
                summary.get("enabled", True)
            )

            status_text = (
                "Enabled"
                if enabled
                else "Disabled"
            )

            print(
                f" - {analyst_id:<12}: "
                f"{opinion} "
                f"({confidence:.0f}) "
                f"[{status_text}]"
            )
    else:
        print(" None")

    print()
    print("Reasons")

    if decision_result.reasons:
        for item in decision_result.reasons:
            print(f" + {item}")
    else:
        print(" None")

    print()
    print("Warnings")

    if decision_result.warnings:
        for item in decision_result.warnings:
            print(f" - {item}")
    else:
        print(" None")

    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()