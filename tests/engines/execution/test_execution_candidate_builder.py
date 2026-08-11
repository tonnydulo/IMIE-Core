import pytest

from imie.engines.execution import ExecutionCandidateBuilder
from imie.models import (
    DecisionResult,
    DirectorDecision,
    PositionSizeResult,
    TradePlan,
)


def make_trade_plan() -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        strategy="Pullback-to-Core",
        direction="long",
        valid=True,
        actionable=True,
        decision="READY",
        entry=100.60,
        stop=99.80,
        target1=101.40,
        target2=102.20,
        risk_per_share=0.80,
        reward1_per_share=0.80,
        reward2_per_share=1.60,
        rr1=1.0,
        rr2=2.0,
        quality=90,
        confidence=90.0,
        reasons=[
            "Trade plan approved.",
        ],
    )


def make_decision() -> DecisionResult:
    return DecisionResult(
        decision=DirectorDecision.READY,
        actionable=True,
        confidence=90.0,
        recommendation=(
            "Take the validated setup."
        ),
        reasons=(
            "Decision Director approved execution.",
        ),
        warnings=(),
        analyst_summary={},
        trade_plan=make_trade_plan(),
        institutional_context=None,
    )


def make_position_size(
    *,
    quantity: int = 156,
    actionable: bool = True,
) -> PositionSizeResult:
    return PositionSizeResult(
        symbol="NVDA",
        direction="long",
        account_equity=25_000.0,
        risk_percent=0.50,
        risk_budget=125.00,
        entry=100.60,
        stop=99.80,
        risk_per_share=0.80,
        quantity=quantity,
        position_notional=(
            quantity * 100.60
        ),
        actual_risk=(
            quantity * 0.80
        ),
        actual_risk_percent=(
            (quantity * 0.80)
            / 25_000.0
            * 100.0
        ),
        valid=True,
        actionable=actionable,
        reasons=(
            "Position size calculated.",
        ),
        warnings=(),
    )


def test_builds_actionable_execution_candidate() -> None:
    candidate = ExecutionCandidateBuilder().build(
        decision=make_decision(),
        position_size=make_position_size(),
    )

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
    assert candidate.target1 == pytest.approx(
        101.40
    )
    assert candidate.target2 == pytest.approx(
        102.20
    )
    assert candidate.position_notional == pytest.approx(
        15_693.60
    )
    assert candidate.risk_amount == pytest.approx(
        124.80
    )
    assert candidate.valid is True
    assert candidate.actionable is True


def test_non_actionable_position_size_blocks_execution() -> None:
    candidate = ExecutionCandidateBuilder().build(
        decision=make_decision(),
        position_size=make_position_size(
            quantity=0,
            actionable=False,
        ),
    )

    assert candidate.quantity == 0
    assert candidate.actionable is False


def test_symbol_mismatch_is_rejected() -> None:
    position_size = make_position_size()

    mismatched = PositionSizeResult(
        symbol="AAPL",
        direction=position_size.direction,
        account_equity=position_size.account_equity,
        risk_percent=position_size.risk_percent,
        risk_budget=position_size.risk_budget,
        entry=position_size.entry,
        stop=position_size.stop,
        risk_per_share=position_size.risk_per_share,
        quantity=position_size.quantity,
        position_notional=position_size.position_notional,
        actual_risk=position_size.actual_risk,
        actual_risk_percent=(
            position_size.actual_risk_percent
        ),
        valid=position_size.valid,
        actionable=position_size.actionable,
    )

    with pytest.raises(
        ValueError,
        match="symbols must match",
    ):
        ExecutionCandidateBuilder().build(
            decision=make_decision(),
            position_size=mismatched,
        )


def test_direction_mismatch_is_rejected() -> None:
    position_size = make_position_size()

    mismatched = PositionSizeResult(
        symbol=position_size.symbol,
        direction="short",
        account_equity=position_size.account_equity,
        risk_percent=position_size.risk_percent,
        risk_budget=position_size.risk_budget,
        entry=position_size.entry,
        stop=position_size.stop,
        risk_per_share=position_size.risk_per_share,
        quantity=position_size.quantity,
        position_notional=position_size.position_notional,
        actual_risk=position_size.actual_risk,
        actual_risk_percent=(
            position_size.actual_risk_percent
        ),
        valid=position_size.valid,
        actionable=position_size.actionable,
    )

    with pytest.raises(
        ValueError,
        match="directions must match",
    ):
        ExecutionCandidateBuilder().build(
            decision=make_decision(),
            position_size=mismatched,
        )