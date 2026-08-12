from __future__ import annotations

from imie.models import (
    ExecutionCandidate,
    ExecutionOrderIntent,
)


class ExecutionOrderIntentBuilder:
    def __init__(
        self,
        *,
        order_type: str = "limit",
        time_in_force: str = "day",
    ) -> None:
        if not isinstance(
            order_type,
            str,
        ):
            raise TypeError(
                "order_type must be a string."
            )

        normalized_order_type = (
            order_type
            .strip()
            .lower()
        )

        if normalized_order_type not in {
            "market",
            "limit",
        }:
            raise ValueError(
                "order_type must be "
                "'market' or 'limit'."
            )

        if not isinstance(
            time_in_force,
            str,
        ):
            raise TypeError(
                "time_in_force must be a string."
            )

        normalized_time_in_force = (
            time_in_force
            .strip()
            .lower()
        )

        if normalized_time_in_force not in {
            "day",
            "gtc",
        }:
            raise ValueError(
                "time_in_force must be "
                "'day' or 'gtc'."
            )

        self.order_type = normalized_order_type
        self.time_in_force = normalized_time_in_force

    def build(
        self,
        *,
        candidate: ExecutionCandidate,
    ) -> ExecutionOrderIntent:
        if not isinstance(
            candidate,
            ExecutionCandidate,
        ):
            raise TypeError(
                "candidate must be an ExecutionCandidate."
            )

        side = (
            "buy"
            if candidate.direction == "long"
            else "sell"
        )

        entry_price = (
            candidate.entry
            if self.order_type == "limit"
            else None
        )

        return ExecutionOrderIntent(
            symbol=candidate.symbol,
            side=side,
            quantity=candidate.quantity,
            order_type=self.order_type,
            entry_price=entry_price,
            stop_price=candidate.stop,
            target1_price=candidate.target1,
            target2_price=candidate.target2,
            time_in_force=self.time_in_force,
            valid=candidate.valid,
            actionable=candidate.actionable,
            reasons=tuple(
                candidate.reasons
            ),
            warnings=tuple(
                candidate.warnings
            ),
        )