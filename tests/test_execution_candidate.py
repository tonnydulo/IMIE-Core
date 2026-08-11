import pytest

from imie.models import ExecutionCandidate


def make_candidate(
    **overrides,
) -> ExecutionCandidate:
    values = {
        "symbol": "NVDA",
        "strategy": "Pullback-to-Core",
        "direction": "long",
        "quantity": 156,
        "entry": 100.60,
        "stop": 99.80,
        "target1": 101.40,
        "target2": 102.20,
        "position_notional": 15_693.60,
        "risk_amount": 124.80,
        "valid": True,
        "actionable": True,
        "reasons": (
            "Trade plan and position size are approved.",
        ),
        "warnings": (),
    }
    values.update(overrides)

    return ExecutionCandidate(
        **values,
    )


def test_execution_candidate_can_be_created() -> None:
    candidate = make_candidate()

    assert candidate.symbol == "NVDA"
    assert candidate.strategy == "Pullback-to-Core"
    assert candidate.direction == "long"
    assert candidate.quantity == 156
    assert candidate.entry == pytest.approx(
        100.60
    )
    assert candidate.stop == pytest.approx(
        99.80
    )
    assert candidate.position_notional == pytest.approx(
        15_693.60
    )
    assert candidate.risk_amount == pytest.approx(
        124.80
    )
    assert candidate.valid is True
    assert candidate.actionable is True


def test_symbol_and_direction_are_normalized() -> None:
    candidate = make_candidate(
        symbol=" nvda ",
        direction=" LONG ",
    )

    assert candidate.symbol == "NVDA"
    assert candidate.direction == "long"


def test_actionable_candidate_requires_positive_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="positive quantity",
    ):
        make_candidate(
            quantity=0,
            actionable=True,
        )


def test_non_actionable_candidate_can_have_zero_quantity() -> None:
    candidate = make_candidate(
        quantity=0,
        position_notional=0.0,
        risk_amount=0.0,
        actionable=False,
    )

    assert candidate.quantity == 0
    assert candidate.actionable is False


@pytest.mark.parametrize(
    "field_name",
    (
        "entry",
        "stop",
        "target1",
        "target2",
    ),
)
def test_prices_must_be_positive(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        make_candidate(
            **{
                field_name: 0.0,
            }
        )