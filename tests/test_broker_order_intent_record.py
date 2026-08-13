from datetime import datetime, timezone

import pytest

from imie.models import (
    BrokerOrderIntentRecord,
    ExecutionOrderIntent,
)


NOW = datetime(2026, 8, 13, 19, 0, tzinfo=timezone.utc)


def make_intent(**overrides: object) -> ExecutionOrderIntent:
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 40,
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


def test_record_normalizes_identity_and_exposes_key() -> None:
    record = BrokerOrderIntentRecord(
        broker=" ALPACA-PAPER ",
        broker_order_id=" order-123 ",
        intent=make_intent(),
        recorded_at=NOW,
        submission_label=" TARGET1 ",
    )

    assert record.broker == "alpaca-paper"
    assert record.broker_order_id == "order-123"
    assert record.submission_label == "target1"
    assert record.key == ("alpaca-paper", "order-123")
    assert record.intent.quantity == 40


def test_record_preserves_exact_slice_quantity() -> None:
    first = BrokerOrderIntentRecord(
        broker="alpaca-paper",
        broker_order_id="order-1",
        intent=make_intent(quantity=40),
        recorded_at=NOW,
        submission_label="target1",
    )
    second = BrokerOrderIntentRecord(
        broker="alpaca-paper",
        broker_order_id="order-2",
        intent=make_intent(quantity=60),
        recorded_at=NOW,
        submission_label="target2",
    )

    assert first.intent.quantity == 40
    assert second.intent.quantity == 60


@pytest.mark.parametrize("valid, actionable", [(False, False), (True, False)])
def test_record_requires_submitted_actionable_intent(
    valid: bool,
    actionable: bool,
) -> None:
    with pytest.raises(ValueError, match="valid and actionable"):
        BrokerOrderIntentRecord(
            broker="alpaca-paper",
            broker_order_id="order-123",
            intent=make_intent(
                valid=valid,
                actionable=actionable,
                quantity=0 if not actionable else 40,
            ),
            recorded_at=NOW,
        )


def test_recorded_at_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        BrokerOrderIntentRecord(
            broker="alpaca-paper",
            broker_order_id="order-123",
            intent=make_intent(),
            recorded_at=datetime(2026, 8, 13, 19, 0),
        )


def test_submission_label_is_constrained() -> None:
    with pytest.raises(ValueError, match="submission_label"):
        BrokerOrderIntentRecord(
            broker="alpaca-paper",
            broker_order_id="order-123",
            intent=make_intent(),
            recorded_at=NOW,
            submission_label="unknown-slice",
        )

