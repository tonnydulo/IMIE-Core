from datetime import datetime, timezone

import pytest

from imie.engines.risk import RiskAnalyst
from imie.models import (
    AcceptanceResult,
    AnalystResult,
    DataFreshness,
    MarketBar,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    SetupLifecycle,
    TradingContext,
)
from imie.utils.constants import LIFECYCLE_READY


def build_context(price: float = 100.60) -> TradingContext:
    timestamp = datetime(2026, 7, 9, 14, 32, tzinfo=timezone.utc)

    bar = MarketBar(
        symbol="TEST",
        timestamp=timestamp,
        open=100.00,
        high=100.70,
        low=99.80,
        close=price,
        volume=10_000,
        timeframe="2m",
        provider="test",
    )

    quote = Quote(
        symbol="TEST",
        timestamp=timestamp,
        bid=price - 0.01,
        ask=price + 0.01,
        last=price,
        provider="test",
    )

    snapshot = MarketSnapshot(
        symbol="TEST",
        timestamp=timestamp,
        quote=quote,
        bars=[bar],
        timeframe="2m",
    )

    return TradingContext(
        snapshot=snapshot,
        measurements=MarketMeasurements(
            price=price,
            ema9=100.00,
            vwap=99.90,
            atr14=1.00,
        ),
        observations=MarketObservations(
            within_core_zone=True,
        ),
    )


def fresh_data() -> DataFreshness:
    timestamp = datetime(2026, 7, 9, 14, 32, tzinfo=timezone.utc)

    return DataFreshness(
        checked_at=timestamp,
        quote_timestamp=timestamp,
        latest_bar_timestamp=timestamp,
        quote_age_seconds=0,
        bar_age_seconds=0,
        quote_bar_gap_seconds=0,
        quote_is_fresh=True,
        bar_is_fresh=True,
        timestamps_aligned=True,
        actionable=True,
        status="FRESH",
        reason="Data is fresh.",
    )


def stale_data() -> DataFreshness:
    result = fresh_data()

    return DataFreshness(
        checked_at=result.checked_at,
        quote_timestamp=result.quote_timestamp,
        latest_bar_timestamp=result.latest_bar_timestamp,
        quote_age_seconds=600,
        bar_age_seconds=600,
        quote_bar_gap_seconds=0,
        quote_is_fresh=False,
        bar_is_fresh=False,
        timestamps_aligned=True,
        actionable=False,
        status="STALE",
        reason="Latest quote and bar are stale.",
    )


def trend_result(opinion: str = "BULLISH") -> AnalystResult:
    return AnalystResult(
        analyst="TrendAnalyst",
        opinion=opinion,
        confidence=90,
        evidence=["Trend confirmed."],
    )


def ready_lifecycle(direction: str) -> SetupLifecycle:
    return SetupLifecycle(
        symbol="TEST",
        state=LIFECYCLE_READY,
        direction=direction,
        confidence=90,
        atr_distance=0.10,
        action="Evaluate entry",
        reason="Acceptance confirmed.",
    )


def long_acceptance() -> AcceptanceResult:
    return AcceptanceResult(
        symbol="TEST",
        accepted=True,
        direction="long",
        level="STRONG",
        score=80,
        confidence=80,
        trigger_price=100.60,
        previous_level=100.50,
        pullback_low=99.80,
        pullback_high=100.50,
        evidence=["Closed above prior high."],
        reason="Long acceptance confirmed.",
    )


def short_acceptance() -> AcceptanceResult:
    return AcceptanceResult(
        symbol="TEST",
        accepted=True,
        direction="short",
        level="STRONG",
        score=80,
        confidence=80,
        trigger_price=99.40,
        previous_level=99.50,
        pullback_low=99.50,
        pullback_high=100.20,
        evidence=["Closed below prior low."],
        reason="Short acceptance confirmed.",
    )


def test_long_trade_plan_uses_pullback_low_as_stop() -> None:
    plan = RiskAnalyst().analyze(
        context=build_context(),
        freshness=fresh_data(),
        trend_result=trend_result(),
        lifecycle=ready_lifecycle("long"),
        acceptance=long_acceptance(),
    )

    assert plan.actionable is True
    assert plan.decision == "READY"
    assert plan.entry == pytest.approx(100.60)
    assert plan.stop == pytest.approx(99.80)
    assert plan.risk_per_share == pytest.approx(0.80)
    assert plan.target1 == pytest.approx(101.40)
    assert plan.target2 == pytest.approx(102.20)
    assert plan.rr2 == pytest.approx(2.0)


def test_short_trade_plan_uses_pullback_high_as_stop() -> None:
    plan = RiskAnalyst().analyze(
        context=build_context(price=99.40),
        freshness=fresh_data(),
        trend_result=trend_result("BEARISH"),
        lifecycle=ready_lifecycle("short"),
        acceptance=short_acceptance(),
    )

    assert plan.actionable is True
    assert plan.entry == pytest.approx(99.40)
    assert plan.stop == pytest.approx(100.20)
    assert plan.risk_per_share == pytest.approx(0.80)
    assert plan.target1 == pytest.approx(98.60)
    assert plan.target2 == pytest.approx(97.80)
    assert plan.rr2 == pytest.approx(2.0)


def test_stale_data_blocks_trade_plan() -> None:
    plan = RiskAnalyst().analyze(
        context=build_context(),
        freshness=stale_data(),
        trend_result=trend_result(),
        lifecycle=ready_lifecycle("long"),
        acceptance=long_acceptance(),
    )

    assert plan.actionable is False
    assert plan.decision == "PASS"
    assert plan.entry is None


def test_missing_acceptance_returns_wait() -> None:
    acceptance = long_acceptance()

    missing_acceptance = AcceptanceResult(
        symbol=acceptance.symbol,
        accepted=False,
        direction=acceptance.direction,
        level="NONE",
        score=0,
        confidence=0,
        trigger_price=None,
        previous_level=acceptance.previous_level,
        pullback_low=acceptance.pullback_low,
        pullback_high=acceptance.pullback_high,
        reason="Acceptance missing.",
    )

    plan = RiskAnalyst().analyze(
        context=build_context(),
        freshness=fresh_data(),
        trend_result=trend_result(),
        lifecycle=ready_lifecycle("long"),
        acceptance=missing_acceptance,
    )

    assert plan.actionable is False
    assert plan.decision == "WAIT"
    assert plan.entry is None


def test_invalid_long_stop_is_rejected() -> None:
    acceptance = long_acceptance()

    invalid_acceptance = AcceptanceResult(
        symbol=acceptance.symbol,
        accepted=True,
        direction="long",
        level="GOOD",
        score=60,
        confidence=60,
        trigger_price=100.60,
        previous_level=100.50,
        pullback_low=100.70,
        pullback_high=100.80,
        reason="Test invalid stop.",
    )

    plan = RiskAnalyst().analyze(
        context=build_context(),
        freshness=fresh_data(),
        trend_result=trend_result(),
        lifecycle=ready_lifecycle("long"),
        acceptance=invalid_acceptance,
    )

    assert plan.actionable is False
    assert plan.decision == "PASS"
    assert plan.stop is None
