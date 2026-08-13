from __future__ import annotations

import json

from collections.abc import Callable
from typing import Any

from imie.models import ExecutionReconciliationResult


class JsonReconciliationResultPublisher:
    """Serialize one explicitly requested reconciliation result."""

    def __init__(
        self,
        *,
        output: Callable[[str], None] = print,
        indent: int | None = None,
        sort_keys: bool = True,
    ) -> None:
        if not callable(output):
            raise TypeError("output must be callable.")
        if indent is not None and (
            isinstance(indent, bool) or not isinstance(indent, int)
        ):
            raise TypeError("indent must be an int or None.")
        if indent is not None and indent < 0:
            raise ValueError("indent cannot be negative.")
        if not isinstance(sort_keys, bool):
            raise TypeError("sort_keys must be a bool.")
        self.output = output
        self.indent = indent
        self.sort_keys = sort_keys

    def __call__(self, result: ExecutionReconciliationResult) -> None:
        self.publish(result)

    def publish(self, result: ExecutionReconciliationResult) -> None:
        self.output(self.dumps(result))

    def dumps(self, result: ExecutionReconciliationResult) -> str:
        return json.dumps(
            self.to_dict(result),
            indent=self.indent,
            sort_keys=self.sort_keys,
            allow_nan=False,
        )

    @staticmethod
    def to_dict(result: ExecutionReconciliationResult) -> dict[str, Any]:
        if not isinstance(result, ExecutionReconciliationResult):
            raise TypeError(
                "result must be an ExecutionReconciliationResult."
            )
        return {
            "broker": result.broker,
            "broker_order_id": result.broker_order_id,
            "symbol": result.symbol,
            "side": result.side,
            "status": result.status.value,
            "intent_quantity": result.intent_quantity,
            "broker_requested_quantity": result.broker_requested_quantity,
            "broker_filled_quantity": result.broker_filled_quantity,
            "recorded_fill_quantity": result.recorded_fill_quantity,
            "broker_average_fill_price": result.broker_average_fill_price,
            "recorded_average_fill_price": result.recorded_average_fill_price,
            "identity_matched": result.identity_matched,
            "quantity_matched": result.quantity_matched,
            "fills_matched": result.fills_matched,
            "reconciled": result.reconciled,
            "discrepancies": list(result.discrepancies),
            "warnings": list(result.warnings),
        }

