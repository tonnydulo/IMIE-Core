import pytest

from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
)

from imie.execution import (
    AlpacaProtectedOrderRequestBuilder,
    ProtectedExecutionPlanBuilder,
)
from imie.models import (
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
    values.update(overrides)
    return ExecutionOrderIntent(**values)


def make_plan(
    **overrides: object,
):
    return ProtectedExecutionPlanBuilder().build(
        make_intent(**overrides)
    )


def test_limit_plan_builds_two_protected_brackets() -> None:
    requests = AlpacaProtectedOrderRequestBuilder().build(
        make_plan()
    )

    assert len(requests) == 2
    assert all(
        isinstance(request, LimitOrderRequest)
        for request in requests
    )
    assert tuple(
        request.qty
        for request in requests
    ) == (63, 62)
    assert tuple(
        request.take_profit.limit_price
        for request in requests
        if request.take_profit is not None
    ) == (501.0, 502.0)

    for request in requests:
        assert request.symbol == "NVDA"
        assert request.side is OrderSide.BUY
        assert request.time_in_force is TimeInForce.DAY
        assert request.order_class is OrderClass.BRACKET
        assert request.limit_price == 500.0
        assert request.stop_loss is not None
        assert request.stop_loss.stop_price == 499.0


def test_market_short_plan_builds_protected_brackets() -> None:
    requests = AlpacaProtectedOrderRequestBuilder().build(
        make_plan(
            side="sell",
            order_type="market",
            entry_price=None,
            time_in_force="gtc",
        )
    )

    assert len(requests) == 2

    for request in requests:
        assert isinstance(request, MarketOrderRequest)
        assert request.side is OrderSide.SELL
        assert request.time_in_force is TimeInForce.GTC
        assert request.order_class is OrderClass.BRACKET
        assert request.stop_loss is not None
        assert request.stop_loss.stop_price == 499.0


def test_single_share_builds_one_target1_bracket() -> None:
    requests = AlpacaProtectedOrderRequestBuilder().build(
        make_plan(quantity=1)
    )

    assert len(requests) == 1
    assert requests[0].qty == 1
    assert requests[0].take_profit is not None
    assert requests[0].take_profit.limit_price == 501.0


def test_total_request_quantity_matches_plan() -> None:
    plan = make_plan(quantity=126)
    requests = AlpacaProtectedOrderRequestBuilder().build(
        plan
    )

    assert sum(
        int(request.qty or 0)
        for request in requests
    ) == plan.quantity == 126


@pytest.mark.parametrize(
    ("valid", "actionable"),
    [
        (False, False),
        (True, False),
    ],
)
def test_non_actionable_plan_is_rejected_before_translation(
    valid: bool,
    actionable: bool,
) -> None:
    plan = make_plan(
        valid=valid,
        actionable=actionable,
    )

    with pytest.raises(
        ValueError,
        match="valid and actionable",
    ):
        AlpacaProtectedOrderRequestBuilder().build(
            plan
        )


def test_invalid_plan_type_raises() -> None:
    with pytest.raises(
        TypeError,
        match="ProtectedExecutionPlan",
    ):
        AlpacaProtectedOrderRequestBuilder().build(
            object()  # type: ignore[arg-type]
        )
