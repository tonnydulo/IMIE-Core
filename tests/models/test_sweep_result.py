from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    SweepDirection,
    SweepResult,
)


def make_pool(
    *,
    side: LiquiditySide = LiquiditySide.BUY_SIDE,
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
        importance=LiquidityImportance.MINOR,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=90.0,
        state=LiquidityState.ACTIVE,
        reason="Confirmed equal liquidity.",
        evidence=("Confirmed liquidity.",),
        source="TestDetector",
    )

    return LiquidityPool(
        price=550.00,
        upper=550.05,
        lower=549.95,
        side=side,
        importance=LiquidityImportance.MINOR,
        confidence=92.0,
        strength=4.0,
        findings=(finding,),
        reason="Liquidity pool.",
        evidence=("Liquidity pool.",),
    )


def make_bearish_sweep() -> SweepResult:
    return SweepResult(
        pool=make_pool(
            side=LiquiditySide.BUY_SIDE,
        ),
        swept=True,
        direction=SweepDirection.BEARISH,
        penetration_price=550.12,
        close_price=549.98,
        reclaimed=True,
        confidence=94.0,
        reason=(
            "Price traded above buy-side liquidity and "
            "closed back below the pool."
        ),
        evidence=(
            "High penetrated the pool upper boundary.",
            "Completed close reclaimed the pool.",
        ),
        warnings=(),
    )


def test_sweep_result_fields() -> None:
    result = make_bearish_sweep()

    assert result.swept is True
    assert result.direction is SweepDirection.BEARISH
    assert result.penetration_price == 550.12
    assert result.close_price == 549.98
    assert result.reclaimed is True
    assert result.confidence == 94.0


def test_sweep_result_is_frozen() -> None:
    result = make_bearish_sweep()

    with pytest.raises(FrozenInstanceError):
        result.confidence = 50.0  # type: ignore[misc]


def test_bearish_helper() -> None:
    result = make_bearish_sweep()

    assert result.is_bearish is True
    assert result.is_bullish is False
    assert result.is_no_sweep is False


def test_bullish_helper() -> None:
    result = SweepResult(
        pool=make_pool(
            side=LiquiditySide.SELL_SIDE,
        ),
        swept=True,
        direction=SweepDirection.BULLISH,
        penetration_price=549.80,
        close_price=550.02,
        reclaimed=True,
        confidence=93.0,
        reason=(
            "Price traded below sell-side liquidity and "
            "closed back above the pool."
        ),
        evidence=(
            "Low penetrated the pool lower boundary.",
            "Completed close reclaimed the pool.",
        ),
        warnings=(),
    )

    assert result.is_bullish is True
    assert result.is_bearish is False


def test_no_sweep_result() -> None:
    result = SweepResult(
        pool=make_pool(),
        swept=False,
        direction=SweepDirection.NONE,
        penetration_price=None,
        close_price=549.90,
        reclaimed=False,
        confidence=80.0,
        reason="Price did not sweep the liquidity pool.",
        evidence=("No qualifying penetration and reclaim.",),
        warnings=(),
    )

    assert result.is_no_sweep is True
    assert result.is_bullish is False
    assert result.is_bearish is False


def test_confirmed_sweep_requires_direction() -> None:
    with pytest.raises(
        ValueError,
        match="must have a direction",
    ):
        SweepResult(
            pool=make_pool(),
            swept=True,
            direction=SweepDirection.NONE,
            penetration_price=550.10,
            close_price=549.98,
            reclaimed=True,
            confidence=90.0,
            reason="Sweep.",
            evidence=("Sweep.",),
            warnings=(),
        )


def test_confirmed_sweep_requires_penetration_price() -> None:
    with pytest.raises(
        ValueError,
        match="penetration_price",
    ):
        SweepResult(
            pool=make_pool(),
            swept=True,
            direction=SweepDirection.BEARISH,
            penetration_price=None,
            close_price=549.98,
            reclaimed=True,
            confidence=90.0,
            reason="Sweep.",
            evidence=("Sweep.",),
            warnings=(),
        )


def test_confirmed_sweep_requires_reclaim() -> None:
    with pytest.raises(
        ValueError,
        match="must reclaim",
    ):
        SweepResult(
            pool=make_pool(),
            swept=True,
            direction=SweepDirection.BEARISH,
            penetration_price=550.10,
            close_price=550.08,
            reclaimed=False,
            confidence=90.0,
            reason="Sweep.",
            evidence=("Sweep.",),
            warnings=(),
        )


def test_non_sweep_requires_none_direction() -> None:
    with pytest.raises(
        ValueError,
        match="must use SweepDirection.NONE",
    ):
        SweepResult(
            pool=make_pool(),
            swept=False,
            direction=SweepDirection.BEARISH,
            penetration_price=None,
            close_price=549.90,
            reclaimed=False,
            confidence=70.0,
            reason="No sweep.",
            evidence=("No sweep.",),
            warnings=(),
        )


def test_non_sweep_cannot_be_reclaimed() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be reclaimed",
    ):
        SweepResult(
            pool=make_pool(),
            swept=False,
            direction=SweepDirection.NONE,
            penetration_price=None,
            close_price=549.90,
            reclaimed=True,
            confidence=70.0,
            reason="No sweep.",
            evidence=("No sweep.",),
            warnings=(),
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -1.0,
        101.0,
    ],
)
def test_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 100",
    ):
        SweepResult(
            pool=make_pool(),
            swept=False,
            direction=SweepDirection.NONE,
            penetration_price=None,
            close_price=549.90,
            reclaimed=False,
            confidence=confidence,
            reason="No sweep.",
            evidence=("No sweep.",),
            warnings=(),
        )