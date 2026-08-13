from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import PositionStateEngine
from imie.models import BrokerFill, ExecutionPosition, PositionDirection


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def position(
    direction: PositionDirection = PositionDirection.FLAT,
    quantity: int = 0,
    entry: float | None = None,
    realized: float = 0.0,
) -> ExecutionPosition:
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=direction,
        quantity=quantity,
        average_entry_price=entry,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=realized,
        last_updated_at=NOW,
    )


def fill(
    fill_id: str,
    side: str,
    quantity: int,
    price: float,
    seconds: int,
    **overrides: object,
) -> BrokerFill:
    values = {
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "fill_id": fill_id,
        "symbol": "NVDA",
        "side": side,
        "quantity": quantity,
        "price": price,
        "executed_at": NOW + timedelta(seconds=seconds),
    }
    values.update(overrides)
    return BrokerFill(**values)


def test_opens_long_position_from_flat() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(),
        fills=(fill("fill-1", "buy", 40, 200.0, 1),),
        market_price=201.0,
    )

    assert result.direction is PositionDirection.LONG
    assert result.quantity == 40
    assert result.average_entry_price == 200.0
    assert result.unrealized_pnl == 40.0


def test_weighted_long_addition() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(PositionDirection.LONG, 40, 200.0),
        fills=(fill("fill-1", "buy", 60, 202.0, 1),),
    )

    assert result.quantity == 100
    assert result.average_entry_price == pytest.approx(201.2)


def test_partial_long_exit_realizes_pnl_and_keeps_entry() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(PositionDirection.LONG, 100, 200.0, realized=5.0),
        fills=(fill("fill-1", "sell", 40, 203.0, 1),),
    )

    assert result.quantity == 60
    assert result.average_entry_price == 200.0
    assert result.realized_pnl == 125.0


def test_full_short_exit_realizes_pnl_and_returns_flat() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(PositionDirection.SHORT, 40, 200.0),
        fills=(fill("fill-1", "buy", 40, 197.0, 1),),
    )

    assert result.direction is PositionDirection.FLAT
    assert result.average_entry_price is None
    assert result.realized_pnl == 120.0


def test_over_close_reverses_long_to_short_at_fill_price() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(PositionDirection.LONG, 40, 200.0),
        fills=(fill("fill-1", "sell", 60, 203.0, 1),),
        market_price=202.0,
    )

    assert result.direction is PositionDirection.SHORT
    assert result.quantity == 20
    assert result.average_entry_price == 203.0
    assert result.realized_pnl == 120.0
    assert result.unrealized_pnl == 20.0


def test_multiple_fills_are_applied_chronologically() -> None:
    result = PositionStateEngine().apply_fills(
        position=position(),
        fills=(
            fill("fill-1", "buy", 40, 200.0, 1),
            fill("fill-2", "buy", 60, 202.0, 2),
            fill("fill-3", "sell", 25, 204.0, 3),
        ),
    )

    assert result.quantity == 75
    assert result.average_entry_price == pytest.approx(201.2)
    assert result.realized_pnl == pytest.approx(70.0)
    assert result.last_updated_at == NOW + timedelta(seconds=3)


def test_empty_fill_set_preserves_position() -> None:
    original = position(PositionDirection.LONG, 40, 200.0)
    result = PositionStateEngine().apply_fills(position=original, fills=())

    assert result == original


def test_already_processed_fill_is_not_applied_twice() -> None:
    first = PositionStateEngine().apply_fills(
        position=position(),
        fills=(fill("fill-1", "buy", 40, 200.0, 1),),
    )

    result = PositionStateEngine().apply_fills(
        position=first,
        fills=(fill("fill-1", "buy", 40, 200.0, 1),),
    )

    assert result == first
    assert result.processed_fill_ids == ("fill-1",)


def test_only_new_fills_are_applied_from_complete_broker_history() -> None:
    first = PositionStateEngine().apply_fills(
        position=position(),
        fills=(fill("fill-1", "buy", 40, 200.0, 1),),
    )

    result = PositionStateEngine().apply_fills(
        position=first,
        fills=(
            fill("fill-1", "buy", 40, 200.0, 1),
            fill("fill-2", "buy", 10, 202.0, 2),
        ),
    )

    assert result.quantity == 50
    assert result.average_entry_price == pytest.approx(200.4)
    assert result.processed_fill_ids == ("fill-1", "fill-2")


@pytest.mark.parametrize(
    "fills, message",
    [
        (
            (fill("duplicate", "buy", 10, 200.0, 1),
             fill("duplicate", "buy", 10, 200.0, 2)),
            "duplicate fill_id",
        ),
        (
            (fill("fill-2", "buy", 10, 200.0, 2),
             fill("fill-1", "buy", 10, 200.0, 1)),
            "chronological",
        ),
        (
            (fill("fill-1", "buy", 10, 200.0, 1, symbol="AMD"),),
            "broker and symbol",
        ),
    ],
)
def test_invalid_fill_sequence_is_rejected(
    fills: tuple[BrokerFill, ...],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        PositionStateEngine().apply_fills(position=position(), fills=fills)
