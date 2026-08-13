import pytest

from imie.execution import ExecutionSafetySubmissionService
from imie.models import (
    BrokerSubmissionResult,
    ExecutionCandidate,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
)


def candidate(**overrides):
    values = {
        "symbol": "NVDA",
        "strategy": "Pullback-to-Core",
        "direction": "long",
        "quantity": 10,
        "entry": 200.0,
        "stop": 199.0,
        "target1": 201.0,
        "target2": 202.0,
        "position_notional": 2_000.0,
        "risk_amount": 10.0,
        "valid": True,
        "actionable": True,
    }
    values.update(overrides)
    return ExecutionCandidate(**values)


def intent(**overrides):
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 10,
        "order_type": "limit",
        "entry_price": 200.0,
        "stop_price": 199.0,
        "target1_price": 201.0,
        "target2_price": 202.0,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
    }
    values.update(overrides)
    return ExecutionOrderIntent(**values)


class Broker:
    def __init__(self, result=None):
        self.calls = []
        self.result = result

    def submit_order(self, value):
        self.calls.append(value)
        return self.result or BrokerSubmissionResult(
            broker="mock",
            symbol=value.symbol,
            side=value.side,
            quantity=value.quantity,
            accepted=True,
            broker_order_id="order-1",
            status="accepted",
            message="Accepted.",
        )


def service(broker, **policy_overrides):
    values = {
        "maximum_order_notional": 5_000.0,
        "maximum_risk_amount": 25.0,
    }
    values.update(policy_overrides)
    return ExecutionSafetySubmissionService(
        broker_execution_port=broker,
        policy=ExecutionSafetyPolicy(**values),
    )


def test_allowed_candidate_is_submitted_exactly_once():
    broker = Broker()
    order_intent = intent()

    result = service(broker).submit(
        candidate=candidate(), intent=order_intent
    )

    assert result.submitted is True
    assert result.broker_submission.accepted is True
    assert broker.calls == [order_intent]


@pytest.mark.parametrize(
    "policy_overrides",
    [
        {"maximum_order_notional": 1_999.0},
        {"maximum_risk_amount": 9.0},
    ],
)
def test_financial_limit_failure_never_reaches_broker(policy_overrides):
    broker = Broker()

    result = service(broker, **policy_overrides).submit(
        candidate=candidate(), intent=intent()
    )

    assert result.submitted is False
    assert result.assessment.allowed is False
    assert broker.calls == []


def test_non_actionable_pair_never_reaches_broker():
    broker = Broker()
    value = candidate(valid=True, actionable=False, quantity=0)
    order_intent = intent(valid=True, actionable=False, quantity=0)

    result = service(broker).submit(candidate=value, intent=order_intent)

    assert result.submitted is False
    assert broker.calls == []


@pytest.mark.parametrize(
    "intent_overrides, mismatch",
    [
        ({"symbol": "AAPL"}, "symbol"),
        ({"side": "sell"}, "side"),
        ({"quantity": 9}, "quantity"),
        ({"entry_price": 200.5}, "entry"),
        ({"stop_price": 198.5}, "stop"),
        ({"target1_price": 201.5}, "target1"),
        ({"target2_price": 202.5}, "target2"),
        ({"valid": False, "actionable": False, "quantity": 0}, "quantity"),
    ],
)
def test_candidate_intent_mismatch_fails_before_broker(
    intent_overrides, mismatch
):
    broker = Broker()

    with pytest.raises(ValueError, match=mismatch):
        service(broker).submit(
            candidate=candidate(), intent=intent(**intent_overrides)
        )

    assert broker.calls == []


def test_market_intent_does_not_require_candidate_entry_mapping():
    broker = Broker()

    result = service(broker).submit(
        candidate=candidate(),
        intent=intent(order_type="market", entry_price=None),
    )

    assert result.submitted is True


def test_short_candidate_requires_sell_intent():
    broker = Broker()

    result = service(broker).submit(
        candidate=candidate(
            direction="short", stop=201.0, target1=199.0, target2=198.0
        ),
        intent=intent(
            side="sell", stop_price=201.0, target1_price=199.0,
            target2_price=198.0,
        ),
    )

    assert result.submitted is True
    assert broker.calls[0].side == "sell"


def test_mismatched_broker_response_fails_visibly():
    broker = Broker(
        BrokerSubmissionResult(
            broker="mock",
            symbol="AAPL",
            side="buy",
            quantity=10,
            accepted=True,
            broker_order_id="order-1",
            status="accepted",
            message="Accepted.",
        )
    )

    with pytest.raises(ValueError, match="identity"):
        service(broker).submit(candidate=candidate(), intent=intent())

    assert len(broker.calls) == 1


def test_invalid_broker_result_type_fails_visibly():
    broker = Broker(result="not-a-result")

    with pytest.raises(TypeError, match="BrokerSubmissionResult"):
        service(broker).submit(candidate=candidate(), intent=intent())
