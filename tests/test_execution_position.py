from datetime import datetime, timezone

import pytest

from imie.models import ExecutionPosition, PositionDirection


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def test_position_direction_values() -> None:
    assert [item.value for item in PositionDirection] == [
        "flat",
        "long",
        "short",
    ]


def test_long_position_normalizes_and_calculates_identity() -> None:
    position = ExecutionPosition(
        broker=" ALPACA-PAPER ",
        symbol=" nvda ",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=201.0,
        market_price=202.5,
        unrealized_pnl=60.0,
        realized_pnl=15.0,
        last_updated_at=NOW,
        warnings=(" delayed quote ", ""),
    )

    assert position.broker == "alpaca-paper"
    assert position.symbol == "NVDA"
    assert position.signed_quantity == 40
    assert position.is_flat is False
    assert position.warnings == ("delayed quote",)


def test_short_position_uses_inverse_unrealized_pnl() -> None:
    position = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.SHORT,
        quantity=40,
        average_entry_price=201.0,
        market_price=199.5,
        unrealized_pnl=60.0,
        realized_pnl=-5.0,
        last_updated_at=NOW,
    )

    assert position.signed_quantity == -40


def test_open_position_may_omit_market_price_before_valuation() -> None:
    position = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=201.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
    )

    assert position.market_price is None


def test_flat_position_preserves_realized_pnl() -> None:
    position = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.FLAT,
        quantity=0,
        average_entry_price=None,
        market_price=202.0,
        unrealized_pnl=0.0,
        realized_pnl=125.5,
        last_updated_at=NOW,
    )

    assert position.is_flat is True
    assert position.signed_quantity == 0
    assert position.realized_pnl == 125.5


@pytest.mark.parametrize(
    "arguments, message",
    [
        (
            {
                "direction": PositionDirection.FLAT,
                "quantity": 1,
                "average_entry_price": None,
                "market_price": None,
                "unrealized_pnl": 0.0,
            },
            "flat position must have zero quantity",
        ),
        (
            {
                "direction": PositionDirection.LONG,
                "quantity": 0,
                "average_entry_price": None,
                "market_price": None,
                "unrealized_pnl": 0.0,
            },
            "requires positive quantity",
        ),
        (
            {
                "direction": PositionDirection.LONG,
                "quantity": 40,
                "average_entry_price": 201.0,
                "market_price": 202.0,
                "unrealized_pnl": 39.0,
            },
            "unrealized_pnl does not match",
        ),
    ],
)
def test_inconsistent_position_state_is_rejected(
    arguments: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ExecutionPosition(
            broker="alpaca-paper",
            symbol="NVDA",
            realized_pnl=0.0,
            last_updated_at=NOW,
            **arguments,
        )


def test_timestamp_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ExecutionPosition(
            broker="alpaca-paper",
            symbol="NVDA",
            direction=PositionDirection.FLAT,
            quantity=0,
            average_entry_price=None,
            market_price=None,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            last_updated_at=datetime(2026, 8, 13, 20, 0),
        )


def test_direction_requires_enum() -> None:
    with pytest.raises(TypeError, match="PositionDirection"):
        ExecutionPosition(
            broker="alpaca-paper",
            symbol="NVDA",
            direction="long",  # type: ignore[arg-type]
            quantity=40,
            average_entry_price=201.0,
            market_price=202.0,
            unrealized_pnl=40.0,
            realized_pnl=0.0,
            last_updated_at=NOW,
        )

