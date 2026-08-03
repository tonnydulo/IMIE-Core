from datetime import datetime, timezone

from imie.engines.structure.core import BosEngine
from imie.models import MarketBar, Swing


def make_bar(
    *,
    index: int,
    close: float,
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

    return MarketBar(
        symbol="SPY",
        timeframe="2m",
        timestamp=timestamp,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def test_detects_bullish_bos_on_completed_close():
    bars = [
        make_bar(
            index=0,
            close=99.0,
            high=100.0,
            low=98.0,
        ),
        make_bar(
            index=1,
            close=101.0,
            high=102.0,
            low=99.0,
        ),
    ]

    highs = [
        Swing(
            index=0,
            price=100.0,
            kind="HIGH",
            strength=2,
        )
    ]

    lows = [
        Swing(
            index=0,
            price=95.0,
            kind="LOW",
            strength=2,
        )
    ]

    result = BosEngine().evaluate(
        bars=bars,
        highs=highs,
        lows=lows,
    )

    assert result.detected is True
    assert result.bullish_break is True
    assert result.bearish_break is False
    assert result.bullish_break_level == 100.0
    assert result.bearish_break_level is None
    assert result.confirmation_price == 101.0


def test_detects_bearish_bos_on_completed_close():
    bars = [
        make_bar(
            index=0,
            close=96.0,
            high=98.0,
            low=95.0,
        ),
        make_bar(
            index=1,
            close=94.0,
            high=96.0,
            low=93.0,
        ),
    ]

    highs = [
        Swing(
            index=0,
            price=100.0,
            kind="HIGH",
            strength=2,
        )
    ]

    lows = [
        Swing(
            index=0,
            price=95.0,
            kind="LOW",
            strength=2,
        )
    ]

    result = BosEngine().evaluate(
        bars=bars,
        highs=highs,
        lows=lows,
    )

    assert result.detected is True
    assert result.bullish_break is False
    assert result.bearish_break is True
    assert result.bullish_break_level is None
    assert result.bearish_break_level == 95.0
    assert result.confirmation_price == 94.0


def test_ignores_wick_only_break():
    bars = [
        make_bar(
            index=0,
            close=99.0,
            high=100.0,
            low=98.0,
        ),
        make_bar(
            index=1,
            close=99.5,
            high=101.0,
            low=98.5,
        ),
    ]

    highs = [
        Swing(
            index=0,
            price=100.0,
            kind="HIGH",
            strength=2,
        )
    ]

    lows = [
        Swing(
            index=0,
            price=95.0,
            kind="LOW",
            strength=2,
        )
    ]

    result = BosEngine().evaluate(
        bars=bars,
        highs=highs,
        lows=lows,
    )

    assert result.detected is False
    assert result.bullish_break is False
    assert result.bearish_break is False
    assert result.bullish_break_level is None
    assert result.bearish_break_level is None
    assert result.confirmation_price is None


def test_returns_no_break_without_swings():
    bars = [
        make_bar(
            index=0,
            close=100.0,
            high=101.0,
            low=99.0,
        )
    ]

    result = BosEngine().evaluate(
        bars=bars,
        highs=[],
        lows=[],
    )

    assert result.detected is False
    assert result.bullish_break is False
    assert result.bearish_break is False
    assert result.confirmation_price is None