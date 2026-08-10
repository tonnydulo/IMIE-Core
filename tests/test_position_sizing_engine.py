import pytest

from imie.engines.position_sizing import PositionSizingEngine
from imie.models import TradePlan


def actionable_trade_plan() -> TradePlan:
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
    )


def test_calculates_position_size_from_default_risk_percent() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
    )

    assert result.risk_percent == pytest.approx(
        0.50
    )

    assert result.risk_budget == pytest.approx(
        125.00
    )

    assert result.quantity == 156

    assert result.position_notional == pytest.approx(
        15_693.60
    )

    assert result.actual_risk == pytest.approx(
        124.80
    )

    assert result.actual_risk_percent == pytest.approx(
        0.4992
    )

    assert result.valid is True
    assert result.actionable is True
    assert result.warnings == ()


def test_custom_risk_percent_overrides_default() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
        risk_percent=0.25,
    )

    assert result.risk_budget == pytest.approx(
        62.50
    )

    assert result.quantity == 78

    assert result.actual_risk == pytest.approx(
        62.40
    )


def test_insufficient_budget_returns_non_actionable_result() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=100.0,
        risk_percent=0.50,
    )

    assert result.risk_budget == pytest.approx(
        0.50
    )

    assert result.quantity == 0
    assert result.actual_risk == pytest.approx(
        0.0
    )

    assert result.valid is True
    assert result.actionable is False

    assert (
        "Risk budget is insufficient for one share."
        in result.warnings
    )


def test_rejects_non_actionable_trade_plan() -> None:
    plan = TradePlan(
        symbol="NVDA",
        strategy="Pullback-to-Core",
        direction="long",
        valid=True,
        actionable=False,
        decision="PASS",
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
    )

    with pytest.raises(
        ValueError,
        match="TradePlan must be valid and actionable",
    ):
        PositionSizingEngine().calculate(
            plan,
            account_equity=25_000.0,
        )


@pytest.mark.parametrize(
    "account_equity,risk_percent",
    [
        (0.0, 0.50),
        (-1.0, 0.50),
        (25_000.0, 0.0),
        (25_000.0, -0.50),
    ],
)
def test_rejects_invalid_account_risk_inputs(
    account_equity: float,
    risk_percent: float,
) -> None:
    with pytest.raises(ValueError):
        PositionSizingEngine().calculate(
            actionable_trade_plan(),
            account_equity=account_equity,
            risk_percent=risk_percent,
        )

def test_buying_power_constrains_position_size() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
        buying_power=10_000.0,
    )

    assert result.risk_budget == pytest.approx(
        125.00
    )

    assert result.quantity == 99

    assert result.position_notional == pytest.approx(
        9_959.40
    )

    assert result.actual_risk == pytest.approx(
        79.20
    )

    assert result.actual_risk_percent == pytest.approx(
        0.3168
    )

    assert result.valid is True
    assert result.actionable is True

    assert (
        "Position size was constrained by available buying power."
        in result.warnings
    )


def test_maximum_notional_constrains_position_size() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
        maximum_notional=5_000.0,
    )

    assert result.quantity == 49

    assert result.position_notional == pytest.approx(
        4_929.40
    )

    assert result.actual_risk == pytest.approx(
        39.20
    )

    assert (
        "Position size was constrained by the maximum "
        "notional limit."
        in result.warnings
    )


def test_tightest_cap_controls_final_quantity() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
        buying_power=10_000.0,
        maximum_notional=5_000.0,
    )

    assert result.quantity == 49

    assert result.position_notional == pytest.approx(
        4_929.40
    )

    assert result.actual_risk == pytest.approx(
        39.20
    )

    assert (
        "Position size was constrained by available buying power."
        in result.warnings
    )

    assert (
        "Position size was constrained by the maximum "
        "notional limit."
        in result.warnings
    )


def test_cap_below_one_share_returns_non_actionable_result() -> None:
    result = PositionSizingEngine().calculate(
        actionable_trade_plan(),
        account_equity=25_000.0,
        buying_power=50.0,
    )

    assert result.quantity == 0
    assert result.position_notional == pytest.approx(
        0.0
    )

    assert result.actual_risk == pytest.approx(
        0.0
    )

    assert result.valid is True
    assert result.actionable is False

    assert (
        "Capital constraints do not allow one share."
        in result.warnings
    )


@pytest.mark.parametrize(
    "buying_power,maximum_notional",
    [
        (0.0, None),
        (-1.0, None),
        (None, 0.0),
        (None, -1.0),
    ],
)
def test_rejects_invalid_capital_constraints(
    buying_power: float | None,
    maximum_notional: float | None,
) -> None:
    with pytest.raises(ValueError):
        PositionSizingEngine().calculate(
            actionable_trade_plan(),
            account_equity=25_000.0,
            buying_power=buying_power,
            maximum_notional=maximum_notional,
        )
