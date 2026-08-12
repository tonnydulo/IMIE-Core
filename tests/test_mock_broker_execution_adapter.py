import pytest

from imie.execution import (
    BrokerExecutionPort,
    MockBrokerExecutionAdapter,
)
from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)


def make_intent(
    **overrides: object,
) -> ExecutionOrderIntent:
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 125,
        "order_type": "limit",
        "entry_price": 500.0,
        "stop_price": 499.0,
        "target1_price": 501.0,
        "target2_price": 502.0,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
    }

    values.update(
        overrides
    )

    return ExecutionOrderIntent(
        **values
    )


def test_mock_adapter_satisfies_execution_port() -> None:
    adapter: BrokerExecutionPort = (
        MockBrokerExecutionAdapter()
    )

    result = adapter.submit_order(
        make_intent()
    )

    assert isinstance(
        result,
        BrokerSubmissionResult,
    )


def test_mock_adapter_accepts_actionable_order() -> None:
    adapter = MockBrokerExecutionAdapter()

    result = adapter.submit_order(
        make_intent()
    )

    assert result.broker == "mock"
    assert result.symbol == "NVDA"
    assert result.side == "buy"
    assert result.quantity == 125
    assert result.accepted is True
    assert result.status == "accepted"
    assert result.broker_order_id == (
        "mock-nvda-000001"
    )


def test_mock_adapter_generates_sequential_order_ids() -> None:
    adapter = MockBrokerExecutionAdapter()

    first = adapter.submit_order(
        make_intent()
    )
    second = adapter.submit_order(
        make_intent()
    )

    assert first.broker_order_id == (
        "mock-nvda-000001"
    )
    assert second.broker_order_id == (
        "mock-nvda-000002"
    )


def test_mock_adapter_rejects_non_actionable_order() -> None:
    adapter = MockBrokerExecutionAdapter()

    result = adapter.submit_order(
        make_intent(
            actionable=False,
            quantity=0,
        )
    )

    assert result.accepted is False
    assert result.status == "rejected"
    assert result.broker_order_id is None


def test_mock_adapter_normalizes_broker_name() -> None:
    adapter = MockBrokerExecutionAdapter(
        broker_name=" TEST ",
    )

    assert adapter.broker_name == "test"


def test_mock_adapter_rejects_empty_broker_name() -> None:
    with pytest.raises(
        ValueError,
        match="broker_name cannot be empty",
    ):
        MockBrokerExecutionAdapter(
            broker_name="   "
        )


def test_mock_adapter_rejects_invalid_intent_type() -> None:
    adapter = MockBrokerExecutionAdapter()

    with pytest.raises(
        TypeError,
        match=(
            "intent must be an ExecutionOrderIntent"
        ),
    ):
        adapter.submit_order(
            object()
        )