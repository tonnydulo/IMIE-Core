from __future__ import annotations

from datetime import UTC, datetime

from imie.directors.decision_director import (
    DecisionDirector,
    DecisionDirectorConfig,
)
from imie.models import (
    DataFreshness,
    DirectorDecision,
    MarketBar,
    MarketFacts,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    TradingContext,
)
from imie.services import AnalysisPipeline


def make_bar(
    *,
    minute: int,
    open_price: float,
    high: float,
    low: float,
    close: float,
    volume: int = 10_000,
) -> MarketBar:
    return MarketBar(
        symbol="NVDA",
        timestamp=datetime(
            2026,
            7,
            9,
            14,
            minute,
            tzinfo=UTC,
        ),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=volume,
        timeframe="2m",
        provider="test",
    )


def make_ready_context() -> TradingContext:
    bars = [
        make_bar(
            minute=16,
            open_price=99.40,
            high=99.70,
            low=99.30,
            close=99.60,
        ),
        make_bar(
            minute=18,
            open_price=99.60,
            high=99.90,
            low=99.50,
            close=99.80,
        ),
        make_bar(
            minute=20,
            open_price=99.80,
            high=100.10,
            low=99.70,
            close=100.00,
        ),
        make_bar(
            minute=22,
            open_price=100.00,
            high=100.30,
            low=99.90,
            close=100.20,
        ),
        make_bar(
            minute=24,
            open_price=100.20,
            high=100.40,
            low=100.00,
            close=100.30,
        ),
        make_bar(
            minute=26,
            open_price=100.30,
            high=100.45,
            low=100.00,
            close=100.20,
        ),
        make_bar(
            minute=28,
            open_price=100.20,
            high=100.50,
            low=99.80,
            close=100.00,
        ),
        make_bar(
            minute=30,
            open_price=100.00,
            high=100.70,
            low=99.95,
            close=100.60,
            volume=12_000,
        ),
    ]

    current_bar = bars[-1]

    quote = Quote(
        symbol="NVDA",
        timestamp=current_bar.timestamp,
        bid=100.59,
        ask=100.61,
        last=current_bar.close,
        provider="test",
    )

    snapshot = MarketSnapshot(
        symbol="NVDA",
        timestamp=current_bar.timestamp,
        quote=quote,
        bars=bars,
        timeframe="2m",
        facts=MarketFacts(
            ema9=100.50,
            vwap=100.20,
            atr14=1.00,
        ),
    )

    measurements = MarketMeasurements(
        price=100.60,
        ema9=100.50,
        previous_ema9=100.40,
        ema9_slope=0.10,
        vwap=100.20,
        atr14=1.00,
        nearest_core="EMA9",
        nearest_core_price=100.50,
        distance_to_core=0.10,
        atr_distance_to_core=0.10,
        core_tolerance=0.25,
    )

    observations = MarketObservations(
        price_above_ema9=True,
        price_below_ema9=False,
        price_above_vwap=True,
        price_below_vwap=False,
        ema9_rising=True,
        ema9_falling=False,
        within_core_zone=True,
        approaching_core=False,
    )

    return TradingContext(
        snapshot=snapshot,
        measurements=measurements,
        observations=observations,
    )


def make_freshness(
    context: TradingContext,
) -> DataFreshness:
    timestamp = context.snapshot.timestamp

    return DataFreshness(
        status="FRESH",
        actionable=True,
        checked_at=timestamp,
        quote_timestamp=timestamp,
        latest_bar_timestamp=timestamp,
        quote_age_seconds=0.0,
        bar_age_seconds=0.0,
        quote_bar_gap_seconds=0.0,
        quote_is_fresh=True,
        bar_is_fresh=True,
        timestamps_aligned=True,
        reason="Market data is fresh.",
    )


def test_pipeline_can_be_created() -> None:
    pipeline = AnalysisPipeline()

    assert pipeline.trend_analyst is not None
    assert pipeline.lifecycle_engine is not None
    assert pipeline.acceptance_analyst is not None
    assert pipeline.risk_analyst is not None
    assert pipeline.decision_director is not None


def test_pipeline_reaches_ready_after_core_acceptance() -> None:
    context = make_ready_context()

    director = DecisionDirector(
        config=DecisionDirectorConfig(
            institutional_bias_policy="READY",
            confluence_policy="ADVISORY",
            market_phase_policy="ADVISORY",
        )
    )

    pipeline = AnalysisPipeline(
        decision_director=director,
    )

    result = pipeline.evaluate(
        context=context,
        freshness=make_freshness(
            context
        ),
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert result.trade_plan is not None
    assert result.trade_plan.valid is True
    assert result.trade_plan.actionable is True
    assert result.trade_plan.direction == "long"

    assert result.institutional_context is not None

    setup = (
        result.institutional_context
        .setup_lifecycle
    )

    acceptance = (
        result.institutional_context
        .acceptance
    )

    assert setup is not None
    assert setup.state == "READY"
    assert setup.direction == "long"

    assert acceptance is not None
    assert acceptance.accepted is True
    assert acceptance.trigger_price == 100.60
    assert acceptance.pullback_low == 99.80