from __future__ import annotations

from itertools import count

from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)


class MockBrokerExecutionAdapter:
    def __init__(
        self,
        *,
        broker_name: str = "mock",
    ) -> None:
        if not isinstance(
            broker_name,
            str,
        ):
            raise TypeError(
                "broker_name must be a string."
            )

        normalized_broker_name = (
            broker_name.strip().lower()
        )

        if not normalized_broker_name:
            raise ValueError(
                "broker_name cannot be empty."
            )

        self._broker_name = (
            normalized_broker_name
        )
        self._order_sequence = count(
            start=1
        )

    @property
    def broker_name(self) -> str:
        return self._broker_name

    def submit_order(
        self,
        intent: ExecutionOrderIntent,
    ) -> BrokerSubmissionResult:
        if not isinstance(
            intent,
            ExecutionOrderIntent,
        ):
            raise TypeError(
                "intent must be an ExecutionOrderIntent."
            )

        if (
            not intent.valid
            or not intent.actionable
            or intent.quantity <= 0
        ):
            return BrokerSubmissionResult(
                broker=self._broker_name,
                symbol=intent.symbol,
                side=intent.side,
                quantity=intent.quantity,
                accepted=False,
                broker_order_id=None,
                status="rejected",
                message=(
                    "Execution order intent is not actionable."
                ),
                warnings=(
                    "Mock broker did not accept the order.",
                ),
            )

        sequence = next(
            self._order_sequence
        )

        broker_order_id = (
            f"{self._broker_name}-"
            f"{intent.symbol.lower()}-"
            f"{sequence:06d}"
        )

        return BrokerSubmissionResult(
            broker=self._broker_name,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            accepted=True,
            broker_order_id=broker_order_id,
            status="accepted",
            message="Mock order accepted.",
        )