from __future__ import annotations

from collections.abc import Callable

from imie.models import ExecutionReconciliationResult


class ConsoleReconciliationResultPublisher:
    """Render one explicitly requested reconciliation result."""

    def __init__(
        self,
        *,
        output: Callable[[str], None] = print,
    ) -> None:
        if not callable(output):
            raise TypeError("output must be callable.")
        self.output = output

    def __call__(self, result: ExecutionReconciliationResult) -> None:
        self.publish(result)

    def publish(self, result: ExecutionReconciliationResult) -> None:
        for line in self.format_lines(result):
            self.output(line)

    @staticmethod
    def format_lines(
        result: ExecutionReconciliationResult,
    ) -> tuple[str, ...]:
        if not isinstance(result, ExecutionReconciliationResult):
            raise TypeError(
                "result must be an ExecutionReconciliationResult."
            )
        lines = [
            "=" * 60,
            "IMIE Execution Reconciliation",
            f"Broker              : {result.broker}",
            f"Broker Order ID     : {result.broker_order_id}",
            f"Symbol              : {result.symbol}",
            f"Side                : {result.side}",
            f"Broker Status       : {result.status.value}",
            f"Intent Quantity     : {result.intent_quantity}",
            f"Broker Requested Qty: {result.broker_requested_quantity}",
            f"Broker Filled Qty   : {result.broker_filled_quantity}",
            f"Recorded Fill Qty   : {result.recorded_fill_quantity}",
            (
                "Broker Avg Fill     : "
                f"{_format_price(result.broker_average_fill_price)}"
            ),
            (
                "Recorded Avg Fill   : "
                f"{_format_price(result.recorded_average_fill_price)}"
            ),
            f"Identity Matched    : {result.identity_matched}",
            f"Quantity Matched    : {result.quantity_matched}",
            f"Fills Matched       : {result.fills_matched}",
            f"Reconciled          : {result.reconciled}",
        ]
        if result.discrepancies:
            lines.append("Discrepancies       :")
            lines.extend(f" - {item}" for item in result.discrepancies)
        if result.warnings:
            lines.append("Warnings            :")
            lines.extend(f" - {item}" for item in result.warnings)
        return tuple(lines)


def _format_price(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.4f}"
