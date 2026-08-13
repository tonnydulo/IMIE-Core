from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import ExecutionReconciliationEngine
from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    ExecutionOrderIntent,
    ExecutionReconciliationResult,
)


NOW = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


def intent(**overrides: object) -> ExecutionOrderIntent:
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 100,
        "order_type": "limit",
        "entry_price": 201.0,
        "stop_price": 200.0,
        "target1_price": 202.0,
        "target2_price": 203.0,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
    }
    values.update(overrides)
    return ExecutionOrderIntent(**values)


def snapshot(**overrides: object) -> BrokerOrderSnapshot:
    values = {
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "symbol": "NVDA",
        "side": "buy",
        "order_type": "limit",
        "status": BrokerOrderStatus.PARTIALLY_FILLED,
        "requested_quantity": 100,
        "filled_quantity": 40,
        "remaining_quantity": 60,
        "average_fill_price": 201.25,
        "submitted_at": NOW,
        "accepted_at": NOW,
        "last_updated_at": NOW,
    }
    values.update(overrides)
    return BrokerOrderSnapshot(**values)


def fill(
    fill_id: str,
    quantity: int,
    price: float,
    **overrides: object,
) -> BrokerFill:
    values = {
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "fill_id": fill_id,
        "symbol": "NVDA",
        "side": "buy",
        "quantity": quantity,
        "price": price,
        "executed_at": NOW + timedelta(seconds=quantity),
    }
    values.update(overrides)
    return BrokerFill(**values)


def test_matching_partial_fills_reconcile() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(),
        fills=(
            fill("fill-1", 15, 201.0),
            fill("fill-2", 25, 201.4),
        ),
    )

    assert isinstance(result, ExecutionReconciliationResult)
    assert result.reconciled is True
    assert result.identity_matched is True
    assert result.quantity_matched is True
    assert result.fills_matched is True
    assert result.recorded_fill_quantity == 40
    assert result.recorded_average_fill_price == pytest.approx(201.25)
    assert result.discrepancies == ()


def test_unfilled_order_reconciles_without_synthetic_fills() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(
            status=BrokerOrderStatus.ACCEPTED,
            filled_quantity=0,
            remaining_quantity=100,
            average_fill_price=None,
        ),
        fills=(),
    )

    assert result.reconciled is True
    assert result.recorded_average_fill_price is None


def test_identity_and_quantity_mismatches_are_reported() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(
            symbol="AMD",
            side="sell",
            order_type="market",
            requested_quantity=90,
            filled_quantity=0,
            remaining_quantity=90,
            average_fill_price=None,
            status=BrokerOrderStatus.ACCEPTED,
        ),
        fills=(),
    )

    assert result.reconciled is False
    assert result.identity_matched is False
    assert result.quantity_matched is False
    assert any("symbol" in item for item in result.discrepancies)
    assert any("quantity" in item for item in result.discrepancies)


def test_missing_fill_activity_is_not_treated_as_reconciled() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(),
        fills=(),
    )

    assert result.reconciled is False
    assert result.fills_matched is False
    assert any("fill quantity" in item for item in result.discrepancies)
    assert any("weighted fill price" in item for item in result.discrepancies)


def test_fill_identity_mismatch_is_reported() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(),
        fills=(fill("fill-1", 40, 201.25, broker_order_id="other"),),
    )

    assert result.reconciled is False
    assert result.fills_matched is False
    assert any("broker_order_id" in item for item in result.discrepancies)


def test_duplicate_fill_ids_are_reported() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(),
        fills=(
            fill("duplicate", 20, 201.25),
            fill("duplicate", 20, 201.25),
        ),
    )

    assert result.reconciled is False
    assert any("Duplicate fill_id" in item for item in result.discrepancies)


def test_weighted_average_mismatch_is_reported() -> None:
    result = ExecutionReconciliationEngine().reconcile(
        intent=intent(),
        snapshot=snapshot(),
        fills=(fill("fill-1", 40, 202.0),),
    )

    assert result.reconciled is False
    assert result.recorded_average_fill_price == 202.0
    assert any("weighted fill price" in item for item in result.discrepancies)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("intent", object(), "ExecutionOrderIntent"),
        ("snapshot", object(), "BrokerOrderSnapshot"),
        ("fills", [], "tuple of BrokerFill"),
    ],
)
def test_invalid_inputs_raise(
    name: str,
    value: object,
    message: str,
) -> None:
    arguments = {
        "intent": intent(),
        "snapshot": snapshot(),
        "fills": (fill("fill-1", 40, 201.25),),
    }
    arguments[name] = value

    with pytest.raises(TypeError, match=message):
        ExecutionReconciliationEngine().reconcile(**arguments)


def test_result_rejects_false_success() -> None:
    with pytest.raises(ValueError, match="every comparison"):
        ExecutionReconciliationResult(
            broker="alpaca-paper",
            broker_order_id="order-123",
            symbol="NVDA",
            side="buy",
            status=BrokerOrderStatus.ACCEPTED,
            intent_quantity=100,
            broker_requested_quantity=100,
            broker_filled_quantity=0,
            recorded_fill_quantity=0,
            broker_average_fill_price=None,
            recorded_average_fill_price=None,
            identity_matched=False,
            quantity_matched=True,
            fills_matched=True,
            reconciled=True,
        )

