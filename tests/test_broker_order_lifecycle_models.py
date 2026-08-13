from datetime import datetime, timezone

import pytest

from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
    BrokerOrderStatus,
)


NOW = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


def make_snapshot(**overrides) -> BrokerOrderSnapshot:
    values = {
        "broker": " alpaca ",
        "broker_order_id": " order-123 ",
        "client_order_id": " client-123 ",
        "symbol": " nvda ",
        "side": " BUY ",
        "order_type": " LIMIT ",
        "status": BrokerOrderStatus.ACCEPTED,
        "requested_quantity": 100,
        "filled_quantity": 0,
        "remaining_quantity": 100,
        "average_fill_price": None,
        "submitted_at": NOW,
        "accepted_at": NOW,
        "last_updated_at": NOW,
        "warnings": (" delayed update ", ""),
    }
    values.update(overrides)
    return BrokerOrderSnapshot(**values)


def test_order_status_values_are_broker_neutral() -> None:
    assert [status.value for status in BrokerOrderStatus] == [
        "pending_submission",
        "submitted",
        "accepted",
        "partially_filled",
        "filled",
        "pending_cancel",
        "canceled",
        "rejected",
        "expired",
        "replaced",
        "unknown",
    ]


def test_order_snapshot_normalizes_broker_truth() -> None:
    snapshot = make_snapshot()

    assert snapshot.broker == "alpaca"
    assert snapshot.broker_order_id == "order-123"
    assert snapshot.client_order_id == "client-123"
    assert snapshot.symbol == "NVDA"
    assert snapshot.side == "buy"
    assert snapshot.order_type == "limit"
    assert snapshot.warnings == ("delayed update",)


def test_partial_fill_snapshot_is_valid() -> None:
    snapshot = make_snapshot(
        status=BrokerOrderStatus.PARTIALLY_FILLED,
        filled_quantity=40,
        remaining_quantity=60,
        average_fill_price=201.25,
    )

    assert snapshot.filled_quantity == 40
    assert snapshot.remaining_quantity == 60
    assert snapshot.average_fill_price == 201.25


def test_filled_snapshot_requires_complete_quantity() -> None:
    with pytest.raises(ValueError, match="full requested quantity"):
        make_snapshot(
            status=BrokerOrderStatus.FILLED,
            filled_quantity=99,
            remaining_quantity=1,
            average_fill_price=201.25,
        )


def test_quantities_must_reconcile() -> None:
    with pytest.raises(ValueError, match="must equal"):
        make_snapshot(
            filled_quantity=20,
            remaining_quantity=70,
            average_fill_price=201.25,
        )


def test_fill_price_and_quantity_must_agree() -> None:
    with pytest.raises(ValueError, match="requires a filled quantity"):
        make_snapshot(average_fill_price=201.25)

    with pytest.raises(ValueError, match="requires average_fill_price"):
        make_snapshot(filled_quantity=20, remaining_quantity=80)


def test_rejected_snapshot_requires_reason() -> None:
    with pytest.raises(ValueError, match="rejection_reason"):
        make_snapshot(status=BrokerOrderStatus.REJECTED)


def test_snapshot_requires_broker_neutral_status_type() -> None:
    with pytest.raises(TypeError, match="BrokerOrderStatus"):
        make_snapshot(status="accepted")


def test_snapshot_timestamps_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_snapshot(last_updated_at=datetime(2026, 8, 13, 18, 0))


def test_broker_fill_normalizes_values() -> None:
    fill = BrokerFill(
        broker=" ALPACA ",
        broker_order_id=" order-123 ",
        fill_id=" fill-1 ",
        symbol=" nvda ",
        side=" BUY ",
        quantity=40,
        price=201.25,
        executed_at=NOW,
    )

    assert fill.broker == "alpaca"
    assert fill.symbol == "NVDA"
    assert fill.side == "buy"
    assert fill.quantity == 40
    assert fill.price == 201.25


@pytest.mark.parametrize("quantity", [0, -1])
def test_broker_fill_quantity_must_be_positive(quantity: int) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        BrokerFill(
            broker="alpaca",
            broker_order_id="order-123",
            fill_id="fill-1",
            symbol="NVDA",
            side="buy",
            quantity=quantity,
            price=201.25,
            executed_at=NOW,
        )


def test_broker_fill_requires_timezone_aware_execution_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        BrokerFill(
            broker="alpaca",
            broker_order_id="order-123",
            fill_id="fill-1",
            symbol="NVDA",
            side="buy",
            quantity=40,
            price=201.25,
            executed_at=datetime(2026, 8, 13, 18, 0),
        )

