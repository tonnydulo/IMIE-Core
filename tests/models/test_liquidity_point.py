from dataclasses import FrozenInstanceError

import pytest

from imie.models.liquidity_point import LiquidityPoint
from imie.models.liquidity_types import LiquiditySide


def create_point() -> LiquidityPoint:
    return LiquidityPoint(
        price=550.25,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        strength=2,
    )


def test_liquidity_point_fields() -> None:
    point = create_point()

    assert point.price == 550.25
    assert point.side is LiquiditySide.BUY_SIDE
    assert point.first_index == 10
    assert point.second_index == 14
    assert point.strength == 2


def test_liquidity_point_is_frozen() -> None:
    point = create_point()

    with pytest.raises(FrozenInstanceError):
        point.price = 600.0  # type: ignore[misc]


def test_liquidity_point_equality() -> None:
    assert create_point() == create_point()


def test_liquidity_point_kind_is_backward_compatible() -> None:
    point = create_point()

    assert point.kind == "BUY_SIDE"


def test_liquidity_point_side_helpers() -> None:
    buy_side = create_point()

    sell_side = LiquidityPoint(
        price=545.00,
        side=LiquiditySide.SELL_SIDE,
        first_index=20,
        second_index=25,
    )

    assert buy_side.is_buy_side is True
    assert buy_side.is_sell_side is False

    assert sell_side.is_buy_side is False
    assert sell_side.is_sell_side is True


def test_liquidity_point_rejects_non_enum_side() -> None:
    with pytest.raises(
        TypeError,
        match="side must be a LiquiditySide",
    ):
        LiquidityPoint(
            price=550.25,
            side="BUY_SIDE",  # type: ignore[arg-type]
            first_index=10,
            second_index=14,
        )


@pytest.mark.parametrize(
    ("price", "first_index", "second_index", "strength", "message"),
    [
        (
            0.0,
            10,
            14,
            1,
            "price must be positive",
        ),
        (
            -1.0,
            10,
            14,
            1,
            "price must be positive",
        ),
        (
            550.25,
            -1,
            14,
            1,
            "first_index cannot be negative",
        ),
        (
            550.25,
            10,
            -1,
            1,
            "second_index cannot be negative",
        ),
        (
            550.25,
            10,
            10,
            1,
            "second_index must be greater",
        ),
        (
            550.25,
            14,
            10,
            1,
            "second_index must be greater",
        ),
        (
            550.25,
            10,
            14,
            0,
            "strength must be positive",
        ),
    ],
)
def test_liquidity_point_validation(
    price: float,
    first_index: int,
    second_index: int,
    strength: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        LiquidityPoint(
            price=price,
            side=LiquiditySide.BUY_SIDE,
            first_index=first_index,
            second_index=second_index,
            strength=strength,
        )