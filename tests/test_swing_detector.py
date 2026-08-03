from datetime import datetime, timezone

from imie.engines.structure.swing_detector import SwingDetector
from imie.models import MarketBar


def make_bar(
    *,
    index: int,
    high: float,
    low: float,
) -> MarketBar:
    timestamp = datetime(
        2026,
        7,
        10,
        14,
        index,
        tzinfo=timezone.utc,
    )

    open_price = (high + low) / 2
    close_price = open_price

    return MarketBar(
        symbol="SPY",
        timeframe="2m",
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close_price,
        volume=1000,
    )


def test_detects_confirmed_swing_high():
    bars = [
        make_bar(index=0, high=10, low=7),
        make_bar(index=1, high=11, low=8),
        make_bar(index=2, high=15, low=9),
        make_bar(index=3, high=12, low=8),
        make_bar(index=4, high=11, low=7),
    ]

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    swings = detector.detect(bars)

    assert len(swings) == 1
    assert swings[0].kind == "HIGH"
    assert swings[0].index == 2
    assert swings[0].price == 15


def test_detects_confirmed_swing_low():
    bars = [
        make_bar(index=0, high=15, low=10),
        make_bar(index=1, high=14, low=9),
        make_bar(index=2, high=13, low=5),
        make_bar(index=3, high=14, low=8),
        make_bar(index=4, high=15, low=9),
    ]

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    swings = detector.detect(bars)

    assert len(swings) == 1
    assert swings[0].kind == "LOW"
    assert swings[0].index == 2
    assert swings[0].price == 5


def test_equal_high_is_not_structural_swing():
    bars = [
        make_bar(index=0, high=10, low=7),
        make_bar(index=1, high=12, low=8),
        make_bar(index=2, high=15, low=9),
        make_bar(index=3, high=15, low=8),
        make_bar(index=4, high=11, low=7),
    ]

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    swings = detector.detect_highs(bars)

    assert swings == ()


def test_returns_empty_when_bars_are_insufficient():
    bars = [
        make_bar(index=0, high=10, low=7),
        make_bar(index=1, high=11, low=8),
        make_bar(index=2, high=12, low=9),
    ]

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    assert detector.detect(bars) == ()