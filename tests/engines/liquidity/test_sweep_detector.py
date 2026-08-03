from __future__ import annotations

import pytest

from imie.engines.liquidity import SweepDetector
from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    MarketBar,
    SweepDirection,
)


def make_bar(
    *,
    high: float,
    low: float,
    close: float,
) -> MarketBar:

    return MarketBar(
        symbol="SPY",
     timeframe="1m",
        timestamp=1,
        open=550.00,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def make_pool(
    *,
    side: LiquiditySide,
) -> LiquidityPool:

    point = LiquidityPoint(
        price=550.00,
        side=side,
        first_index=10,
        second_index=20,
        strength=3,
    )

    finding = LiquidityFinding(
        point=point,
        liquidity_type=(
            LiquidityType.EQUAL_HIGH
            if side is LiquiditySide.BUY_SIDE
            else LiquidityType.EQUAL_LOW
        ),
        importance=LiquidityImportance.MAJOR,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=92.0,
        state=LiquidityState.ACTIVE,
        reason="Liquidity",
        evidence=("Liquidity",),
        source="UnitTest",
    )

    return LiquidityPool(
        price=550.00,
        upper=550.05,
        lower=549.95,
        side=side,
        importance=LiquidityImportance.MAJOR,
        confidence=94.0,
        strength=5.0,
        findings=(finding,),
        reason="Pool",
        evidence=("Pool",),
    )


def test_detects_bearish_sweep() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.10,
        low=549.80,
        close=550.00,
    )

    result = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
            ),
        ),
    )[0]

    assert result.swept is True
    assert result.direction is SweepDirection.BEARISH


def test_detects_bullish_sweep() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.10,
        low=549.90,
        close=550.00,
    )

    result = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.SELL_SIDE,
            ),
        ),
    )[0]

    assert result.swept is True
    assert result.direction is SweepDirection.BULLISH


def test_buy_side_breakout_not_sweep() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.20,
        low=549.90,
        close=550.15,
    )

    result = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
            ),
        ),
    )[0]

    assert result.swept is False
    assert result.direction is SweepDirection.NONE


def test_sell_side_breakout_not_sweep() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.00,
        low=549.80,
        close=549.85,
    )

    result = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.SELL_SIDE,
            ),
        ),
    )[0]

    assert result.swept is False
    assert result.direction is SweepDirection.NONE


def test_touch_only_not_sweep() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.05,
        low=549.95,
        close=550.00,
    )

    result = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
            ),
        ),
    )[0]

    assert result.swept is False


def test_multiple_pools() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.10,
        low=549.90,
        close=550.00,
    )

    results = detector.detect(
        bar,
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
            ),
            make_pool(
                side=LiquiditySide.SELL_SIDE,
            ),
        ),
    )

    assert len(results) == 2


def test_invalid_confidence() -> None:

    with pytest.raises(ValueError):

        SweepDetector(
            confirmed_confidence=120.0,
        )


def test_invalid_bar() -> None:

    detector = SweepDetector()

    with pytest.raises(TypeError):

        detector.detect(
            None,  # type: ignore[arg-type]
            (),
        )


def test_invalid_pool() -> None:

    detector = SweepDetector()

    bar = make_bar(
        high=550.10,
        low=549.90,
        close=550.00,
    )

    with pytest.raises(TypeError):

        detector.detect(
            bar,
            (
                None,  # type: ignore[arg-type]
            ),
        )