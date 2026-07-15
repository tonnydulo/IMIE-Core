from datetime import datetime, timezone

from imie.engines.structure import StructureAnalyst
from imie.engines.structure.core import StructureEngine
from imie.models import (
    MarketBar,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    Swing,
    TradingContext,
)


def make_bar(
    minute: int,
    high: float,
    low: float,
) -> MarketBar:
    timestamp = datetime(
        2026,
        7,
        10,
        14,
        minute,
        tzinfo=timezone.utc,
    )

    price = (high + low) / 2

    return MarketBar(
        symbol="SPY",
        timeframe="2m",
        timestamp=timestamp,
        open=price,
        high=high,
        low=low,
        close=price,
        volume=1000,
    )


def create_context() -> TradingContext:
    bars = [
        make_bar(0, 10, 7),
        make_bar(1, 11, 8),
        make_bar(2, 15, 9),
        make_bar(3, 12, 8),
        make_bar(4, 11, 7),
        make_bar(5, 10, 6),
        make_bar(6, 11, 8),
    ]

    quote = Quote(
        symbol="SPY",
        bid=9.95,
        ask=10.05,
        last=10.00,
        timestamp=bars[-1].timestamp,
    )

    snapshot = MarketSnapshot(
        symbol="SPY",
        timeframe="2m",
        timestamp=bars[-1].timestamp,
        quote=quote,
        bars=bars,
    )

    measurements = MarketMeasurements(
        price=10.0,
    )

    observations = MarketObservations()

    return TradingContext(
        snapshot=snapshot,
        measurements=measurements,
        observations=observations,
    )


def test_structure_analyst_returns_structure_result():
    analyst = StructureAnalyst()

    result = analyst.analyze(
        create_context(),
    )

    structure = result.payload

    assert result.opinion == "STRUCTURE_READY"
    assert structure is not None
    assert structure.swing_high_count == 1
    assert structure.nearest_resistance == 15


def test_infers_bullish_structure():
    highs = [
        Swing(
            index=2,
            price=100.0,
            kind="HIGH",
            strength=2,
        ),
        Swing(
            index=8,
            price=105.0,
            kind="HIGH",
            strength=2,
        ),
    ]

    lows = [
        Swing(
            index=4,
            price=95.0,
            kind="LOW",
            strength=2,
        ),
        Swing(
            index=10,
            price=98.0,
            kind="LOW",
            strength=2,
        ),
    ]

    direction, state, confidence = (
        StructureEngine._infer_structure(
            highs=highs,
            lows=lows,
        )
    )

    assert direction == "long"
    assert state == "BULLISH_STRUCTURE"
    assert confidence == 85.0


def test_infers_bearish_structure():
    highs = [
        Swing(
            index=2,
            price=105.0,
            kind="HIGH",
            strength=2,
        ),
        Swing(
            index=8,
            price=101.0,
            kind="HIGH",
            strength=2,
        ),
    ]

    lows = [
        Swing(
            index=4,
            price=98.0,
            kind="LOW",
            strength=2,
        ),
        Swing(
            index=10,
            price=94.0,
            kind="LOW",
            strength=2,
        ),
    ]

    direction, state, confidence = (
        StructureEngine._infer_structure(
    highs=highs,
    lows=lows,
)
    )

    assert direction == "short"
    assert state == "BEARISH_STRUCTURE"
    assert confidence == 85.0


def test_infers_neutral_structure_when_progression_is_mixed():
    highs = [
        Swing(
            index=2,
            price=100.0,
            kind="HIGH",
            strength=2,
        ),
        Swing(
            index=8,
            price=105.0,
            kind="HIGH",
            strength=2,
        ),
    ]

    lows = [
        Swing(
            index=4,
            price=95.0,
            kind="LOW",
            strength=2,
        ),
        Swing(
            index=10,
            price=92.0,
            kind="LOW",
            strength=2,
        ),
    ]

    direction, state, confidence = (
        StructureEngine._infer_structure(
            highs=highs,
            lows=lows,
        )
    )

    assert direction == "neutral"
    assert state == "NEUTRAL_STRUCTURE"
    assert confidence == 60.0


def test_infers_unconfirmed_structure_when_swings_are_insufficient():
    highs = [
        Swing(
            index=2,
            price=100.0,
            kind="HIGH",
            strength=2,
        ),
    ]

    lows = [
        Swing(
            index=4,
            price=95.0,
            kind="LOW",
            strength=2,
        ),
    ]

    direction, state, confidence = (
        StructureEngine._infer_structure(
            highs=highs,
            lows=lows,
        )
    )

    assert direction == "neutral"
    assert state == "UNCONFIRMED_STRUCTURE"
    assert confidence == 40.0