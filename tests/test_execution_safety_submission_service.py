import pytest
from datetime import datetime, timezone

from imie.execution import ExecutionSafetySubmissionService
from imie.models import (
    BrokerSubmissionResult,
    ExecutionCandidate,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
)


NOW = datetime(2026, 8, 14, 6, 0, tzinfo=timezone.utc)


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


class ReservationStore:
    def __init__(self, error=None):
        self.values = {}
        self.error = error

    def reserve(self, value):
        if self.error:
            raise self.error
        if value.fingerprint in self.values:
            raise ValueError("already reserved")
        self.values[value.fingerprint] = value

    def get(self, fingerprint):
        return self.values.get(fingerprint)


def service(broker, reservation_store=None, **policy_overrides):
    values = {
        "maximum_order_notional": 5_000.0,
        "maximum_risk_amount": 25.0,
    }
    values.update(policy_overrides)
    return ExecutionSafetySubmissionService(
        broker_execution_port=broker,
        policy=ExecutionSafetyPolicy(**values),
        reservation_store=reservation_store or ReservationStore(),
        clock=lambda: NOW,
    )


def test_allowed_candidate_is_submitted_exactly_once():
    broker = Broker()
    order_intent = intent()

    result = service(broker).submit(
        candidate=candidate(), intent=order_intent
    )

    assert result.submitted is True
    assert result.broker_submission.accepted is True
    assert result.reservation.symbol == "NVDA"
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


def test_active_kill_switch_never_reserves_or_reaches_broker():
    broker = Broker()
    reservation_store = ReservationStore()

    result = service(
        broker,
        reservation_store=reservation_store,
        kill_switch_active=True,
    ).submit(candidate=candidate(), intent=intent())

    assert result.submitted is False
    assert result.assessment.kill_switch_active is True
    assert result.reservation is None
    assert reservation_store.values == {}
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


def test_exact_duplicate_is_reserved_before_second_broker_call():
    broker = Broker()
    reservations = ReservationStore()
    guarded = service(broker, reservation_store=reservations)

    guarded.submit(candidate=candidate(), intent=intent())
    with pytest.raises(ValueError, match="already reserved"):
        guarded.submit(candidate=candidate(), intent=intent())

    assert len(broker.calls) == 1


def test_reservation_failure_prevents_broker_mutation():
    broker = Broker()
    reservations = ReservationStore(OSError("disk full"))

    with pytest.raises(OSError, match="disk full"):
        service(broker, reservation_store=reservations).submit(
            candidate=candidate(), intent=intent()
        )

    assert broker.calls == []


def test_broker_exception_leaves_reservation_to_block_retry():
    class FailingBroker(Broker):
        def submit_order(self, value):
            self.calls.append(value)
            raise RuntimeError("broker timeout")

    broker = FailingBroker()
    reservations = ReservationStore()
    guarded = service(broker, reservation_store=reservations)

    with pytest.raises(RuntimeError, match="broker timeout"):
        guarded.submit(candidate=candidate(), intent=intent())
    with pytest.raises(ValueError, match="already reserved"):
        guarded.submit(candidate=candidate(), intent=intent())

    assert len(broker.calls) == 1


def test_changed_order_terms_receive_distinct_reservation():
    broker = Broker()
    reservations = ReservationStore()
    guarded = service(broker, reservation_store=reservations)

    guarded.submit(candidate=candidate(), intent=intent())
    guarded.submit(
        candidate=candidate(quantity=11, position_notional=2_200.0),
        intent=intent(quantity=11),
    )

    assert len(broker.calls) == 2
    assert len(reservations.values) == 2
