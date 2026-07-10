from datetime import datetime, timezone

from imie.engines.acceptance import AcceptanceAnalyst
from imie.models import (
    MarketBar,
    MarketFacts,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    SetupLifecycle,
    TradingContext,
)
from imie.utils.constants import LIFECYCLE_AT_CORE


def make_bar(
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
    minute: int,
) -> MarketBar:
    return MarketBar(
        symbol="TEST",
        timestamp=datetime(
            2026,
            7,
            9,
            14,
            minute,
            tzinfo=timezone.utc,
        ),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=10_000,
        timeframe="2m",
        provider="test",
    )


def build_context(
    previous_bar: MarketBar,
    current_bar: MarketBar,
) -> TradingContext:
    quote = Quote(
        symbol="TEST",
        timestamp=current_bar.timestamp,
        bid=current_bar.close - 0.01,
        ask=current_bar.close + 0.01,
        last=current_bar.close,
        provider="test",
    )

    snapshot = MarketSnapshot(
        symbol="TEST",
        timestamp=current_bar.timestamp,
        quote=quote,
        bars=[previous_bar, current_bar],
        timeframe="2m",
        facts=MarketFacts(
            ema9=100.00,
            vwap=99.90,
            atr14=1.00,
        ),
    )

    return TradingContext(
        snapshot=snapshot,
        measurements=MarketMeasurements(
            price=current_bar.close,
            ema9=100.00,
            vwap=99.90,
            atr14=1.00,
            nearest_core="EMA9",
            nearest_core_price=100.00,
            distance_to_core=0.10,
            atr_distance_to_core=0.10,
            core_tolerance=0.25,
        ),
        observations=MarketObservations(
            within_core_zone=True,
        ),
    )


def make_lifecycle(direction: str) -> SetupLifecycle:
    return SetupLifecycle(
        symbol="TEST",
        state=LIFECYCLE_AT_CORE,
        direction=direction,
        confidence=90,
        atr_distance=0.10,
        action="Prepare",
        reason="At Core.",
    )


def test_long_acceptance_requires_close_above_prior_high() -> None:
    previous_bar = make_bar(
        open_price=100.20,
        high=100.50,
        low=99.80,
        close=100.00,
        minute=30,
    )
    current_bar = make_bar(
        open_price=100.00,
        high=100.70,
        low=99.95,
        close=100.60,
        minute=32,
    )

    result = AcceptanceAnalyst().analyze(
        build_context(previous_bar, current_bar),
        make_lifecycle("long"),
    )

    assert result.accepted is True
    assert result.trigger_price == 100.60
    assert result.previous_level == 100.50
    assert result.score >= 50


def test_long_acceptance_rejects_intrabar_wick_without_close() -> None:
    previous_bar = make_bar(
        open_price=100.20,
        high=100.50,
        low=99.80,
        close=100.00,
        minute=30,
    )
    current_bar = make_bar(
        open_price=100.00,
        high=100.70,
        low=99.95,
        close=100.40,
        minute=32,
    )

    result = AcceptanceAnalyst().analyze(
        build_context(previous_bar, current_bar),
        make_lifecycle("long"),
    )

    assert result.accepted is False
    assert result.score == 0


def test_short_acceptance_requires_close_below_prior_low() -> None:
    previous_bar = make_bar(
        open_price=100.00,
        high=100.30,
        low=99.50,
        close=99.80,
        minute=30,
    )
    current_bar = make_bar(
        open_price=99.80,
        high=99.85,
        low=99.20,
        close=99.30,
        minute=32,
    )

    result = AcceptanceAnalyst().analyze(
        build_context(previous_bar, current_bar),
        make_lifecycle("short"),
    )

    assert result.accepted is True
    assert result.trigger_price == 99.30
    assert result.previous_level == 99.50
    assert result.score >= 50


def test_acceptance_is_not_evaluated_outside_at_core() -> None:
    previous_bar = make_bar(
        open_price=100.20,
        high=100.50,
        low=99.80,
        close=100.00,
        minute=30,
    )
    current_bar = make_bar(
        open_price=100.00,
        high=100.70,
        low=99.95,
        close=100.60,
        minute=32,
    )

    lifecycle = SetupLifecycle(
        symbol="TEST",
        state="TRENDING",
        direction="long",
        confidence=90,
        atr_distance=4.00,
        action="Ignore",
        reason="Not at Core.",
    )

    result = AcceptanceAnalyst().analyze(
        build_context(previous_bar, current_bar),
        lifecycle,
    )

    assert result.accepted is False
    assert "only when price is at Core" in result.reason
