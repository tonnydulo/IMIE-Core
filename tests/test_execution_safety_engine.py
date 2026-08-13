import pytest

from imie.execution import ExecutionSafetyEngine
from imie.models import (
    ExecutionCandidate,
    ExecutionSafetyAssessment,
    ExecutionSafetyPolicy,
)


def candidate(**overrides):
    values = {
        "symbol": "NVDA",
        "strategy": "Pullback-to-Core",
        "direction": "long",
        "quantity": 100,
        "entry": 200.0,
        "stop": 199.0,
        "target1": 201.0,
        "target2": 202.0,
        "position_notional": 20_000.0,
        "risk_amount": 100.0,
        "valid": True,
        "actionable": True,
    }
    values.update(overrides)
    return ExecutionCandidate(**values)


def policy(**overrides):
    values = {
        "maximum_order_notional": 25_000.0,
        "maximum_risk_amount": 125.0,
    }
    values.update(overrides)
    return ExecutionSafetyPolicy(**values)


def test_candidate_within_both_limits_is_allowed():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(), policy=policy()
    )

    assert isinstance(result, ExecutionSafetyAssessment)
    assert result.allowed is True
    assert result.notional_within_limit is True
    assert result.risk_within_limit is True
    assert result.violations == ()


def test_exact_limit_boundaries_are_allowed():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(),
        policy=policy(
            maximum_order_notional=20_000.0,
            maximum_risk_amount=100.0,
        ),
    )

    assert result.allowed is True


def test_notional_over_limit_is_blocked():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(),
        policy=policy(maximum_order_notional=19_999.99),
    )

    assert result.allowed is False
    assert result.notional_within_limit is False
    assert any("Order notional exceeds" in item for item in result.violations)


def test_risk_over_limit_is_blocked():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(),
        policy=policy(maximum_risk_amount=99.99),
    )

    assert result.allowed is False
    assert result.risk_within_limit is False
    assert any("Trade risk exceeds" in item for item in result.violations)


def test_both_limit_violations_are_reported_together():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(),
        policy=policy(
            maximum_order_notional=10_000.0,
            maximum_risk_amount=50.0,
        ),
    )

    assert result.allowed is False
    assert len(result.violations) == 2


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"valid": False, "actionable": False, "quantity": 0}, "invalid"),
        ({"valid": True, "actionable": False, "quantity": 0}, "not actionable"),
    ],
)
def test_non_actionable_candidate_fails_closed(overrides, message):
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(**overrides), policy=policy()
    )

    assert result.allowed is False
    assert any(message in item.lower() for item in result.violations)


def test_candidate_warnings_are_preserved():
    result = ExecutionSafetyEngine().assess(
        candidate=candidate(warnings=("Sizing warning.",)), policy=policy()
    )

    assert result.warnings == ("Sizing warning.",)


@pytest.mark.parametrize(
    "field, value",
    [
        ("maximum_order_notional", 0),
        ("maximum_order_notional", -1),
        ("maximum_order_notional", float("inf")),
        ("maximum_risk_amount", 0),
        ("maximum_risk_amount", True),
    ],
)
def test_policy_requires_finite_positive_limits(field, value):
    with pytest.raises((TypeError, ValueError)):
        policy(**{field: value})


def test_engine_requires_typed_candidate_and_policy():
    engine = ExecutionSafetyEngine()

    with pytest.raises(TypeError, match="candidate"):
        engine.assess(candidate=object(), policy=policy())
    with pytest.raises(TypeError, match="policy"):
        engine.assess(candidate=candidate(), policy=object())
