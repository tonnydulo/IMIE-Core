from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    BrokerPositionProtectionValidator,
    ExistingPositionProtectionPlanBuilder,
    ExistingPositionProtectionService,
    ProtectionAuditPersistenceError,
)
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionOrderIntent,
    ExecutionPosition,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
    PositionProtectionRecord,
    PositionProtectionAttemptStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def position():
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW - timedelta(seconds=10),
        processed_fill_ids=("fill-1",),
    )


def plan(current=None):
    current = current or position()
    return ExistingPositionProtectionPlanBuilder().build(
        intent=ExecutionOrderIntent(
            symbol="NVDA",
            side="buy",
            quantity=40,
            order_type="limit",
            entry_price=200.0,
            stop_price=199.0,
            target1_price=201.0,
            target2_price=202.0,
            time_in_force="gtc",
            valid=True,
            actionable=True,
        ),
        position=current,
        coverage=ProtectiveCoverageAssessment(
            broker="alpaca-paper",
            symbol="NVDA",
            status=ProtectiveCoverageStatus.READY,
            position_quantity=40,
            protected_quantity=0,
            uncovered_quantity=40,
            actionable=True,
            reasons=("Protection required.",),
        ),
    )


def broker_position(**overrides):
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "direction": PositionDirection.LONG,
        "quantity": 40,
        "average_entry_price": 200.0,
        "market_price": 201.0,
        "unrealized_pnl": 40.0,
        "observed_at": NOW,
    }
    values.update(overrides)
    return BrokerPositionSnapshot(**values)


def accepted_result(plan_value):
    return ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=40,
        requested_quantity=40,
        accepted_quantity=40,
        position_updated_at=plan_value.position_updated_at,
        accepted=True,
        status="accepted",
        message="accepted",
        submissions=(
            ExistingPositionProtectionSubmission(
                label="target1",
                quantity=20,
                accepted=True,
                target_order_id="target-1",
                stop_order_id="stop-1",
                status="accepted",
                message="accepted",
            ),
            ExistingPositionProtectionSubmission(
                label="target2",
                quantity=20,
                accepted=True,
                target_order_id="target-2",
                stop_order_id="stop-2",
                status="accepted",
                message="accepted",
            ),
        ),
    )


class Store:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def get(self, *, broker, symbol):
        self.calls.append((broker, symbol))
        return self.value

    def save(self, position):
        self.value = position


class Query:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def get_position(self, symbol):
        self.calls.append(symbol)
        return self.value


class Protection:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def submit_existing_position_protection(self, *, plan, current_position):
        self.calls.append((plan, current_position))
        return self.result


class Ledger:
    def __init__(self, prior=None, save_error=None):
        self.prior = prior
        self.save_error = save_error
        self.get_calls = []
        self.saved = []

    def get_for_position(self, **kwargs):
        self.get_calls.append(kwargs)
        return self.prior

    def save(self, record):
        if self.save_error is not None:
            raise self.save_error
        self.saved.append(record)
        self.prior = record


class Attempts:
    def __init__(self, prior=None, reserve_error=None, transition_error=None):
        self.prior = prior
        self.reserve_error = reserve_error
        self.transition_error = transition_error
        self.reserved = []
        self.transitions = []

    def get_for_position(self, **kwargs):
        return self.prior

    def reserve(self, attempt):
        if self.reserve_error:
            raise self.reserve_error
        self.reserved.append(attempt)
        self.prior = attempt

    def transition(self, attempt):
        if self.transition_error:
            raise self.transition_error
        self.transitions.append(attempt)
        self.prior = attempt


def service(store, query, protection, ledger=None, attempts=None):
    return ExistingPositionProtectionService(
        position_store=store,
        position_query_port=query,
        protection_port=protection,
        protection_store=ledger or Ledger(),
        attempt_store=attempts or Attempts(),
        validator=BrokerPositionProtectionValidator(clock=lambda: NOW),
        clock=lambda: NOW,
        attempt_id_factory=lambda: "attempt-1",
    )


def test_service_validates_two_truths_then_submits_once():
    current = position()
    plan_value = plan(current)
    store = Store(current)
    query = Query(broker_position())
    protection = Protection(accepted_result(plan_value))

    ledger = Ledger()
    attempts = Attempts()
    result = service(store, query, protection, ledger, attempts).protect(plan_value)

    assert result.accepted is True
    assert store.calls == [("alpaca-paper", "NVDA")]
    assert query.calls == ["NVDA"]
    assert protection.calls == [(plan_value, current)]
    assert len(ledger.saved) == 1
    assert ledger.saved[0].result is result
    assert ledger.saved[0].position_fill_ids == ("fill-1",)
    assert ledger.saved[0].recorded_at == NOW
    assert attempts.reserved[0].status is PositionProtectionAttemptStatus.RESERVED
    assert attempts.transitions[0].status is PositionProtectionAttemptStatus.ACCEPTED
    assert attempts.transitions[0].result is result


def test_missing_persisted_position_fails_before_broker_query():
    query = Query(broker_position())
    protection = Protection(None)

    with pytest.raises(LookupError, match="No persisted position"):
        service(Store(None), query, protection).protect(plan())

    assert query.calls == []
    assert protection.calls == []


def test_existing_accepted_record_blocks_before_broker_query_or_submission():
    current = position()
    plan_value = plan(current)
    prior = PositionProtectionRecord(
        result=accepted_result(plan_value),
        position_fill_ids=plan_value.position_fill_ids,
        recorded_at=NOW,
    )
    query = Query(broker_position())
    protection = Protection(accepted_result(plan_value))

    with pytest.raises(RuntimeError, match="already exists"):
        service(Store(current), query, protection, Ledger(prior)).protect(plan_value)

    assert query.calls == []
    assert protection.calls == []


def test_existing_attempt_blocks_before_broker_query_or_submission():
    current = position()
    plan_value = plan(current)
    attempts = Attempts()
    first = service(
        Store(current), Query(broker_position()),
        Protection(accepted_result(plan_value)), Ledger(), attempts,
    )
    first.protect(plan_value)
    query = Query(broker_position())
    protection = Protection(accepted_result(plan_value))

    with pytest.raises(RuntimeError, match="attempt already exists"):
        service(Store(current), query, protection, Ledger(), attempts).protect(plan_value)

    assert query.calls == []
    assert protection.calls == []


def test_rejected_protection_result_is_not_recorded():
    plan_value = plan()
    rejected = ExistingPositionProtectionResult(
        broker="alpaca-paper", symbol="NVDA", exit_side="sell",
        position_quantity=40, requested_quantity=40, accepted_quantity=0,
        position_updated_at=plan_value.position_updated_at,
        accepted=False, status="rejected", message="rejected",
        submissions=tuple(
            ExistingPositionProtectionSubmission(
                label=item.label, quantity=item.quantity, accepted=False,
                target_order_id=None, stop_order_id=None,
                status="rejected", message="rejected",
            ) for item in accepted_result(plan_value).submissions
        ),
    )
    ledger = Ledger()

    attempts = Attempts()
    result = service(
        Store(position()), Query(broker_position()), Protection(rejected), ledger,
        attempts,
    ).protect(plan_value)

    assert result.accepted is False
    assert ledger.saved == []
    assert attempts.transitions[0].status is PositionProtectionAttemptStatus.FAILED


def test_accepted_broker_result_with_audit_failure_raises_critical_error():
    plan_value = plan()
    result_value = accepted_result(plan_value)
    ledger = Ledger(save_error=OSError("disk unavailable"))

    attempts = Attempts()
    with pytest.raises(ProtectionAuditPersistenceError, match="CRITICAL") as caught:
        service(
            Store(position()), Query(broker_position()),
            Protection(result_value), ledger, attempts,
        ).protect(plan_value)

    assert caught.value.result is result_value
    assert isinstance(caught.value.cause, OSError)
    assert "disk unavailable" in str(caught.value)
    assert attempts.transitions[0].status is PositionProtectionAttemptStatus.UNCERTAIN
    assert attempts.transitions[0].result is result_value


def test_transport_exception_transitions_reserved_attempt_to_uncertain():
    class RaisingProtection(Protection):
        def submit_existing_position_protection(self, **kwargs):
            self.calls.append(kwargs)
            raise TimeoutError("broker timeout")

    attempts = Attempts()

    with pytest.raises(TimeoutError, match="broker timeout"):
        service(
            Store(position()), Query(broker_position()),
            RaisingProtection(None), Ledger(), attempts,
        ).protect(plan())

    assert attempts.reserved[0].status is PositionProtectionAttemptStatus.RESERVED
    assert attempts.transitions[0].status is PositionProtectionAttemptStatus.UNCERTAIN
    assert "broker timeout" in attempts.transitions[0].message


def test_reservation_failure_prevents_broker_mutation():
    protection = Protection(accepted_result(plan()))

    with pytest.raises(OSError, match="disk unavailable"):
        service(
            Store(position()), Query(broker_position()), protection, Ledger(),
            Attempts(reserve_error=OSError("disk unavailable")),
        ).protect(plan())

    assert protection.calls == []


@pytest.mark.parametrize(
    "broker_truth",
    [None, broker_position(quantity=39), broker_position(observed_at=NOW - timedelta(seconds=6))],
)
def test_missing_mismatched_or_stale_broker_truth_blocks_submission(broker_truth):
    protection = Protection(None)

    with pytest.raises(ValueError):
        service(Store(position()), Query(broker_truth), protection).protect(plan())

    assert protection.calls == []


def test_changed_persisted_position_blocks_submission():
    protection = Protection(None)
    changed = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=39,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=position().last_updated_at,
        processed_fill_ids=("fill-1",),
    )

    with pytest.raises(ValueError, match="quantity"):
        service(Store(changed), Query(broker_position(quantity=39)), protection).protect(plan())

    assert protection.calls == []
