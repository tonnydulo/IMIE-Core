from __future__ import annotations

from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
from alpaca.trading.requests import (
    LimitOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
)

from imie.execution.existing_position_protection_guard import (
    ExistingPositionProtectionGuard,
)
from imie.models import ExecutionPosition, ExistingPositionProtectionPlan


class AlpacaExistingPositionProtectionRequestBuilder:
    """Translate existing-position protection into exit-side Alpaca OCOs."""

    def __init__(
        self,
        *,
        guard: ExistingPositionProtectionGuard | None = None,
    ) -> None:
        resolved_guard = guard or ExistingPositionProtectionGuard()
        if not isinstance(resolved_guard, ExistingPositionProtectionGuard):
            raise TypeError(
                "guard must be an ExistingPositionProtectionGuard or None."
            )
        self._guard = resolved_guard

    def build(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        current_position: ExecutionPosition,
    ) -> tuple[LimitOrderRequest, ...]:
        self._guard.validate(plan=plan, current_position=current_position)
        requests = tuple(
            LimitOrderRequest(
                symbol=plan.symbol,
                qty=order_slice.quantity,
                side=OrderSide(plan.exit_side),
                time_in_force=TimeInForce(plan.time_in_force),
                order_class=OrderClass.OCO,
                take_profit=TakeProfitRequest(
                    limit_price=order_slice.target_price
                ),
                stop_loss=StopLossRequest(
                    stop_price=order_slice.stop_price
                ),
            )
            for order_slice in plan.slices
        )
        if sum(int(request.qty or 0) for request in requests) != (
            plan.uncovered_quantity
        ):
            raise ValueError(
                "Alpaca OCO quantities do not match uncovered position quantity."
            )
        return requests
