import pytest

from imie.engines.execution import (
    ExecutionOrderIntentBuilder,
)
from imie.models import ExecutionCandidate


def make_candidate(
    *,
    direction: str = "long",
    quantity: int = 100,
    actionable: bool = True,
) -> ExecutionCandidate:
    return ExecutionCandidate(
        symbol="NVDA",
        strategy="PULLBACK_TO_CORE",
        direction=direction,
        quantity=quantity,
        entry=500.00,
        stop=499.00,
        target1=501.00,
        target2=502.00,
        position_notional=50_000.00,
        risk_amount=100.00,
        valid=True,
        actionable=actionable,
        reasons=(
            "Execution candidate approved.",
        ),
        warnings=(),
    )


def test_builder_can_be_created() -> None:
    builder = ExecutionOrderIntentBuilder()

    assert builder.order_type == "limit"
    assert builder.time_in_force == "day"


def test_builds_long_limit_order_intent() -> None:
    builder = ExecutionOrderIntentBuilder()

    intent = builder.build(
        candidate=make_candidate(
            direction="long"
        )
    )

    assert intent.symbol == "NVDA"
    assert intent.side == "buy"
    assert intent.quantity == 100
    assert intent.order_type == "limit"
    assert intent.entry_price == 500.00
    assert intent.stop_price == 499.00
    assert intent.target1_price == 501.00
    assert intent.target2_price == 502.00
    assert intent.time_in_force == "day"
    assert intent.valid is True
    assert intent.actionable is True


def test_builds_short_limit_order_intent() -> None:
    builder = ExecutionOrderIntentBuilder()

    intent = builder.build(
        candidate=make_candidate(
            direction="short"
        )
    )

    assert intent.side == "sell"


def test_market_order_omits_entry_price() -> None:
    builder = ExecutionOrderIntentBuilder(
        order_type="market",
    )

    intent = builder.build(
        candidate=make_candidate()
    )

    assert intent.order_type == "market"
    assert intent.entry_price is None


def test_non_actionable_candidate_remains_non_actionable() -> None:
    builder = ExecutionOrderIntentBuilder()

    intent = builder.build(
        candidate=make_candidate(
            quantity=0,
            actionable=False,
        )
    )

    assert intent.quantity == 0
    assert intent.actionable is False


def test_reasons_and_warnings_are_preserved() -> None:
    candidate = ExecutionCandidate(
        symbol="NVDA",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        quantity=100,
        entry=500.00,
        stop=499.00,
        target1=501.00,
        target2=502.00,
        position_notional=50_000.00,
        risk_amount=100.00,
        valid=True,
        actionable=True,
        reasons=(
            "Execution candidate approved.",
        ),
        warnings=(
            "Test warning.",
        ),
    )

    intent = ExecutionOrderIntentBuilder().build(
        candidate=candidate
    )

    assert intent.reasons == (
        "Execution candidate approved.",
    )
    assert intent.warnings == (
        "Test warning.",
    )


@pytest.mark.parametrize(
    "order_type",
    (
        "",
        "stop",
        "bracket",
    ),
)
def test_invalid_order_type_is_rejected(
    order_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="order_type",
    ):
        ExecutionOrderIntentBuilder(
            order_type=order_type
        )


@pytest.mark.parametrize(
    "time_in_force",
    (
        "",
        "ioc",
        "fok",
    ),
)
def test_invalid_time_in_force_is_rejected(
    time_in_force: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="time_in_force",
    ):
        ExecutionOrderIntentBuilder(
            time_in_force=time_in_force
        )


def test_candidate_must_be_execution_candidate() -> None:
    builder = ExecutionOrderIntentBuilder()

    with pytest.raises(
        TypeError,
        match="ExecutionCandidate",
    ):
        builder.build(
            candidate=object(),  # type: ignore[arg-type]
        )