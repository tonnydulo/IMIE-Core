from imie.execution import ExecutionSubmissionFingerprint
from imie.models import ExecutionCandidate, ExecutionOrderIntent


def candidate(**overrides):
    values = {
        "symbol": "NVDA", "strategy": "Pullback-to-Core",
        "direction": "long", "quantity": 10, "entry": 200.0,
        "stop": 199.0, "target1": 201.0, "target2": 202.0,
        "position_notional": 2_000.0, "risk_amount": 10.0,
        "valid": True, "actionable": True,
    }
    values.update(overrides)
    return ExecutionCandidate(**values)


def intent(**overrides):
    values = {
        "symbol": "NVDA", "side": "buy", "quantity": 10,
        "order_type": "limit", "entry_price": 200.0,
        "stop_price": 199.0, "target1_price": 201.0,
        "target2_price": 202.0, "time_in_force": "day",
        "valid": True, "actionable": True,
    }
    values.update(overrides)
    return ExecutionOrderIntent(**values)


def fingerprint(candidate_value=None, intent_value=None):
    return ExecutionSubmissionFingerprint.create(
        candidate=candidate_value or candidate(),
        intent=intent_value or intent(),
    )


def test_exact_submission_pair_has_stable_sha256_fingerprint():
    first = fingerprint()
    second = fingerprint()

    assert first == second
    assert len(first) == 64
    assert set(first) <= set("0123456789abcdef")


def test_diagnostic_text_does_not_change_execution_identity():
    first = fingerprint(
        candidate(warnings=("first",)), intent(warnings=("first",))
    )
    second = fingerprint(
        candidate(warnings=("second",)), intent(warnings=("second",))
    )

    assert first == second


def test_legitimate_order_changes_create_distinct_fingerprints():
    baseline = fingerprint()
    changed = (
        fingerprint(candidate(quantity=11, position_notional=2_200.0), intent(quantity=11)),
        fingerprint(candidate(stop=198.5), intent(stop_price=198.5)),
        fingerprint(intent_value=intent(time_in_force="gtc")),
        fingerprint(candidate(strategy="Break-and-Retest")),
    )

    assert all(value != baseline for value in changed)
    assert len(set(changed)) == len(changed)
