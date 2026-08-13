from datetime import datetime, timezone

import pytest

from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest

from imie.execution import (
    AlpacaExistingPositionProtectionRequestBuilder,
    ExistingPositionProtectionPlanBuilder,
)
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def position(*, direction=PositionDirection.LONG, quantity=40):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=direction,
        quantity=quantity,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def plan(current, *, protected=0, uncovered=40):
    long = current.direction is PositionDirection.LONG
    intent = ExecutionOrderIntent(
        symbol="NVDA",
        side="buy" if long else "sell",
        quantity=40,
        order_type="limit",
        entry_price=200.0,
        stop_price=199.0 if long else 201.0,
        target1_price=201.0 if long else 199.0,
        target2_price=202.0 if long else 198.0,
        time_in_force="gtc",
        valid=True,
        actionable=True,
    )
    coverage = ProtectiveCoverageAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        status=(
            ProtectiveCoverageStatus.READY
            if protected == 0
            else ProtectiveCoverageStatus.PARTIALLY_PROTECTED
        ),
        position_quantity=protected + uncovered,
        protected_quantity=protected,
        uncovered_quantity=uncovered,
        actionable=True,
        reasons=("Protection required.",),
    )
    return ExistingPositionProtectionPlanBuilder().build(
        intent=intent, position=current, coverage=coverage
    )


def test_long_position_builds_sell_side_oco_exit_requests():
    current = position()
    requests = AlpacaExistingPositionProtectionRequestBuilder().build(
        plan=plan(current), current_position=current
    )

    assert len(requests) == 2
    assert all(isinstance(request, LimitOrderRequest) for request in requests)
    assert tuple(request.qty for request in requests) == (20, 20)
    assert tuple(
        request.take_profit.limit_price for request in requests
    ) == (201.0, 202.0)
    for request in requests:
        assert request.symbol == "NVDA"
        assert request.side is OrderSide.SELL
        assert request.time_in_force is TimeInForce.GTC
        assert request.order_class is OrderClass.OCO
        assert request.stop_loss.stop_price == 199.0


def test_short_position_builds_buy_side_oco_exit_requests():
    current = position(direction=PositionDirection.SHORT)
    requests = AlpacaExistingPositionProtectionRequestBuilder().build(
        plan=plan(current), current_position=current
    )

    assert all(request.side is OrderSide.BUY for request in requests)
    assert tuple(
        request.take_profit.limit_price for request in requests
    ) == (199.0, 198.0)
    assert all(request.stop_loss.stop_price == 201.0 for request in requests)


def test_partial_coverage_translates_only_uncovered_quantity():
    current = position()
    requests = AlpacaExistingPositionProtectionRequestBuilder().build(
        plan=plan(current, protected=25, uncovered=15),
        current_position=current,
    )

    assert tuple(request.qty for request in requests) == (8, 7)
    assert sum(int(request.qty) for request in requests) == 15


def test_changed_position_is_rejected_before_request_translation():
    original = position()
    changed = position(quantity=39)

    with pytest.raises(ValueError, match="quantity"):
        AlpacaExistingPositionProtectionRequestBuilder().build(
            plan=plan(original), current_position=changed
        )


def test_entry_bracket_plan_type_cannot_be_translated():
    current = position()

    with pytest.raises(TypeError, match="ExistingPositionProtectionPlan"):
        AlpacaExistingPositionProtectionRequestBuilder().build(
            plan=object(),  # type: ignore[arg-type]
            current_position=current,
        )
