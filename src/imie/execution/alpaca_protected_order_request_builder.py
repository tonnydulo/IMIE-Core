from __future__ import annotations

from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderRequest,
    StopLossRequest,
    TakeProfitRequest,
)

from imie.models import (
    ProtectedExecutionPlan,
    ProtectedOrderSlice,
)


class AlpacaProtectedOrderRequestBuilder:
    """Translate a protected plan into Alpaca bracket requests."""

    def build(
        self,
        plan: ProtectedExecutionPlan,
    ) -> tuple[OrderRequest, ...]:
        if not isinstance(
            plan,
            ProtectedExecutionPlan,
        ):
            raise TypeError(
                "plan must be a ProtectedExecutionPlan."
            )

        if not plan.valid or not plan.actionable:
            raise ValueError(
                "plan must be valid and actionable."
            )

        requests = tuple(
            self._build_slice_request(
                plan=plan,
                order_slice=order_slice,
            )
            for order_slice in plan.slices
        )

        if sum(
            int(request.qty or 0)
            for request in requests
        ) != plan.quantity:
            raise ValueError(
                "Alpaca request quantities do not match the plan."
            )

        return requests

    @staticmethod
    def _build_slice_request(
        *,
        plan: ProtectedExecutionPlan,
        order_slice: ProtectedOrderSlice,
    ) -> OrderRequest:
        common = {
            "symbol": plan.symbol,
            "qty": order_slice.quantity,
            "side": OrderSide(plan.side),
            "time_in_force": TimeInForce(
                plan.time_in_force
            ),
            "order_class": OrderClass.BRACKET,
            "take_profit": TakeProfitRequest(
                limit_price=order_slice.target_price,
            ),
            "stop_loss": StopLossRequest(
                stop_price=order_slice.stop_price,
            ),
        }

        if plan.order_type == "market":
            return MarketOrderRequest(
                **common
            )

        if plan.entry_price is None:
            raise ValueError(
                "A limit plan requires entry_price."
            )

        return LimitOrderRequest(
            **common,
            limit_price=plan.entry_price,
        )
