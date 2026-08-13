from __future__ import annotations

import math

from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
    ExecutionOrderIntent,
    ExecutionReconciliationResult,
)


class ExecutionReconciliationEngine:
    """Compare an IMIE intent with broker order and fill truth."""

    def reconcile(
        self,
        *,
        intent: ExecutionOrderIntent,
        snapshot: BrokerOrderSnapshot,
        fills: tuple[BrokerFill, ...],
    ) -> ExecutionReconciliationResult:
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        if not isinstance(snapshot, BrokerOrderSnapshot):
            raise TypeError("snapshot must be a BrokerOrderSnapshot.")
        if not isinstance(fills, tuple) or not all(
            isinstance(fill, BrokerFill) for fill in fills
        ):
            raise TypeError("fills must be a tuple of BrokerFill.")

        discrepancies: list[str] = []
        identity_matched = True
        for label, intended, actual in (
            ("symbol", intent.symbol, snapshot.symbol),
            ("side", intent.side, snapshot.side),
            ("order_type", intent.order_type, snapshot.order_type),
        ):
            if intended != actual:
                identity_matched = False
                discrepancies.append(
                    f"Intent {label} {intended!r} does not match broker {actual!r}."
                )

        quantity_matched = intent.quantity == snapshot.requested_quantity
        if not quantity_matched:
            discrepancies.append(
                "Intent quantity does not match broker requested quantity: "
                f"{intent.quantity} != {snapshot.requested_quantity}."
            )

        seen_fill_ids: set[str] = set()
        recorded_quantity = 0
        recorded_notional = 0.0
        fills_matched = True
        for fill in fills:
            if fill.fill_id in seen_fill_ids:
                fills_matched = False
                discrepancies.append(f"Duplicate fill_id {fill.fill_id!r}.")
            seen_fill_ids.add(fill.fill_id)
            for label, expected, actual in (
                ("broker", snapshot.broker, fill.broker),
                ("broker_order_id", snapshot.broker_order_id, fill.broker_order_id),
                ("symbol", snapshot.symbol, fill.symbol),
                ("side", snapshot.side, fill.side),
            ):
                if expected != actual:
                    fills_matched = False
                    discrepancies.append(
                        f"Fill {fill.fill_id!r} {label} does not match snapshot."
                    )
            recorded_quantity += fill.quantity
            recorded_notional += fill.quantity * fill.price

        recorded_average = (
            recorded_notional / recorded_quantity if recorded_quantity else None
        )
        if recorded_quantity != snapshot.filled_quantity:
            fills_matched = False
            discrepancies.append(
                "Recorded fill quantity does not match broker filled quantity: "
                f"{recorded_quantity} != {snapshot.filled_quantity}."
            )
        if not self._prices_match(
            recorded_average,
            snapshot.average_fill_price,
        ):
            fills_matched = False
            discrepancies.append(
                "Recorded weighted fill price does not match broker average fill price."
            )

        reconciled = identity_matched and quantity_matched and fills_matched
        return ExecutionReconciliationResult(
            broker=snapshot.broker,
            broker_order_id=snapshot.broker_order_id,
            symbol=snapshot.symbol,
            side=snapshot.side,
            status=snapshot.status,
            intent_quantity=intent.quantity,
            broker_requested_quantity=snapshot.requested_quantity,
            broker_filled_quantity=snapshot.filled_quantity,
            recorded_fill_quantity=recorded_quantity,
            broker_average_fill_price=snapshot.average_fill_price,
            recorded_average_fill_price=recorded_average,
            identity_matched=identity_matched,
            quantity_matched=quantity_matched,
            fills_matched=fills_matched,
            reconciled=reconciled,
            discrepancies=tuple(discrepancies),
            warnings=snapshot.warnings,
        )

    @staticmethod
    def _prices_match(left: float | None, right: float | None) -> bool:
        if left is None or right is None:
            return left is right
        return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-6)

