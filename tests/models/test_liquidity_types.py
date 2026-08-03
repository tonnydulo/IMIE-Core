from imie.models.liquidity_types import (
    LiquidityImportance,
    LiquidityLocation,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    SweepDirection,
)


def test_liquidity_side_values() -> None:
    assert LiquiditySide.BUY_SIDE.value == "buy_side"
    assert LiquiditySide.SELL_SIDE.value == "sell_side"


def test_liquidity_type_values() -> None:
    assert LiquidityType.EQUAL_HIGH.value == "equal_high"
    assert LiquidityType.EQUAL_LOW.value == "equal_low"
    assert LiquidityType.PREVIOUS_DAY_HIGH.value == "previous_day_high"
    assert LiquidityType.PREVIOUS_WEEK_LOW.value == "previous_week_low"
    assert LiquidityType.OPENING_RANGE_HIGH.value == "opening_range_high"
    assert LiquidityType.PREMARKET_LOW.value == "premarket_low"
    assert LiquidityType.LONDON_HIGH.value == "london_high"
    assert LiquidityType.TOKYO_LOW.value == "tokyo_low"
    assert LiquidityType.INTERNAL_SWING_HIGH.value == "internal_swing_high"
    assert LiquidityType.EXTERNAL_SWING_LOW.value == "external_swing_low"


def test_liquidity_importance_values() -> None:
    assert LiquidityImportance.MAJOR.value == "major"
    assert LiquidityImportance.INTERMEDIATE.value == "intermediate"
    assert LiquidityImportance.MINOR.value == "minor"


def test_liquidity_location_values() -> None:
    assert LiquidityLocation.INTERNAL.value == "internal"
    assert LiquidityLocation.EXTERNAL.value == "external"
    assert LiquidityLocation.UNCLASSIFIED.value == "unclassified"


def test_liquidity_state_values() -> None:
    assert LiquidityState.ACTIVE.value == "active"
    assert LiquidityState.TESTED.value == "tested"
    assert LiquidityState.SWEPT.value == "swept"
    assert LiquidityState.CONSUMED.value == "consumed"
    assert LiquidityState.INVALIDATED.value == "invalidated"


def test_sweep_direction_values() -> None:
    assert SweepDirection.BULLISH.value == "bullish"
    assert SweepDirection.BEARISH.value == "bearish"
    assert SweepDirection.NONE.value == "none"


def test_liquidity_enums_are_string_compatible() -> None:
    assert LiquiditySide.BUY_SIDE == "buy_side"
    assert LiquidityImportance.MAJOR == "major"
    assert LiquidityState.ACTIVE == "active"
    assert SweepDirection.NONE == "none"