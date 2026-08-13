from __future__ import annotations

from typing import Protocol

from alpaca.trading.requests import OrderRequest

from imie.execution.alpaca_existing_position_protection_request_builder import (
    AlpacaExistingPositionProtectionRequestBuilder,
)
from imie.models import (
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
)


class AlpacaProtectionTradingClient(Protocol):
    def submit_order(self, order_data: OrderRequest) -> object:
        ...

    def cancel_order_by_id(self, order_id: str) -> None:
        ...


class AlpacaPaperExistingPositionProtectionAdapter:
    """Submit existing-position exit OCOs to an explicitly gated paper client."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        trading_client: AlpacaProtectionTradingClient,
        paper: bool,
        request_builder: (
            AlpacaExistingPositionProtectionRequestBuilder | None
        ) = None,
    ) -> None:
        if paper is not True:
            raise ValueError("existing-position protection is paper-only.")
        if not callable(getattr(trading_client, "submit_order", None)):
            raise TypeError("trading_client must expose submit_order().")
        if not callable(getattr(trading_client, "cancel_order_by_id", None)):
            raise TypeError("trading_client must expose cancel_order_by_id().")
        builder = request_builder or AlpacaExistingPositionProtectionRequestBuilder()
        if not isinstance(
            builder, AlpacaExistingPositionProtectionRequestBuilder
        ):
            raise TypeError(
                "request_builder must be an "
                "AlpacaExistingPositionProtectionRequestBuilder or None."
            )
        self._trading_client = trading_client
        self._request_builder = builder

    def submit_existing_position_protection(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        current_position: ExecutionPosition,
    ) -> ExistingPositionProtectionResult:
        requests = self._request_builder.build(
            plan=plan,
            current_position=current_position,
        )
        submissions: list[ExistingPositionProtectionSubmission] = []
        accepted_parent_ids: list[str] = []

        for order_slice, request in zip(plan.slices, requests, strict=True):
            parent_id: str | None = None
            try:
                order = self._trading_client.submit_order(order_data=request)
                parent_id = self._optional_id(getattr(order, "id", None))
                status = self._enum_value(getattr(order, "status", "unknown"))
                target_id, stop_id = self._oco_leg_ids(order)
                accepted = (
                    parent_id is not None
                    and status != "rejected"
                    and target_id is not None
                    and stop_id is not None
                )
                submission = ExistingPositionProtectionSubmission(
                    label=order_slice.label,
                    quantity=order_slice.quantity,
                    accepted=accepted,
                    target_order_id=target_id if accepted else None,
                    stop_order_id=stop_id if accepted else None,
                    status=status if accepted else "incomplete",
                    message=(
                        "Alpaca paper OCO protection accepted."
                        if accepted
                        else "Alpaca paper OCO response lacked complete exit legs."
                    ),
                )
            except Exception as exc:
                submission = ExistingPositionProtectionSubmission(
                    label=order_slice.label,
                    quantity=order_slice.quantity,
                    accepted=False,
                    target_order_id=None,
                    stop_order_id=None,
                    status="error",
                    message=f"Alpaca paper OCO submission failed: {exc}",
                )

            submissions.append(submission)
            if parent_id is not None:
                accepted_parent_ids.append(parent_id)
            if not submission.accepted:
                complete_submissions = self._complete_submissions(
                    plan=plan,
                    submissions=tuple(submissions),
                )
                return self._rollback(
                    plan=plan,
                    submissions=complete_submissions,
                    parent_ids=tuple(accepted_parent_ids),
                )

        return ExistingPositionProtectionResult(
            broker=self.broker_name,
            symbol=plan.symbol,
            exit_side=plan.exit_side,
            position_quantity=plan.position_quantity,
            requested_quantity=plan.uncovered_quantity,
            accepted_quantity=plan.uncovered_quantity,
            position_updated_at=plan.position_updated_at,
            accepted=True,
            status="accepted",
            message="All Alpaca paper position-protection OCOs were accepted.",
            submissions=tuple(submissions),
            warnings=plan.warnings,
        )

    @staticmethod
    def _complete_submissions(
        *,
        plan: ExistingPositionProtectionPlan,
        submissions: tuple[ExistingPositionProtectionSubmission, ...],
    ) -> tuple[ExistingPositionProtectionSubmission, ...]:
        completed = list(submissions)
        for order_slice in plan.slices[len(submissions) :]:
            completed.append(
                ExistingPositionProtectionSubmission(
                    label=order_slice.label,
                    quantity=order_slice.quantity,
                    accepted=False,
                    target_order_id=None,
                    stop_order_id=None,
                    status="not_attempted",
                    message="Submission skipped after an earlier OCO failure.",
                )
            )
        return tuple(completed)

    def _rollback(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        submissions: tuple[ExistingPositionProtectionSubmission, ...],
        parent_ids: tuple[str, ...],
    ) -> ExistingPositionProtectionResult:
        accepted_quantity = sum(
            item.quantity for item in submissions if item.accepted
        )
        if not parent_ids:
            return self._failed_result(
                plan=plan,
                submissions=submissions,
                accepted_quantity=accepted_quantity,
                status="rejected",
                message="Alpaca paper rejected position protection.",
            )

        failures = []
        for parent_id in reversed(parent_ids):
            try:
                self._trading_client.cancel_order_by_id(parent_id)
            except Exception as exc:
                failures.append(
                    f"Failed to cancel Alpaca paper OCO {parent_id}: {exc}"
                )
        rollback_succeeded = not failures
        return self._failed_result(
            plan=plan,
            submissions=submissions,
            accepted_quantity=accepted_quantity,
            status="rolled_back" if rollback_succeeded else "rollback_failed",
            message=(
                "Partial position protection was fully rolled back."
                if rollback_succeeded
                else "Partial position protection could not be fully rolled back."
            ),
            rollback_attempted=True,
            rollback_succeeded=rollback_succeeded,
            warnings=tuple(failures),
        )

    def _failed_result(
        self,
        *,
        plan,
        submissions,
        accepted_quantity,
        status,
        message,
        rollback_attempted=False,
        rollback_succeeded=None,
        warnings=(),
    ) -> ExistingPositionProtectionResult:
        return ExistingPositionProtectionResult(
            broker=self.broker_name,
            symbol=plan.symbol,
            exit_side=plan.exit_side,
            position_quantity=plan.position_quantity,
            requested_quantity=sum(item.quantity for item in submissions),
            accepted_quantity=accepted_quantity,
            position_updated_at=plan.position_updated_at,
            accepted=False,
            status=status,
            message=message,
            submissions=submissions,
            rollback_attempted=rollback_attempted,
            rollback_succeeded=rollback_succeeded,
            warnings=plan.warnings + warnings,
        )

    @classmethod
    def _oco_leg_ids(cls, order: object) -> tuple[str | None, str | None]:
        target_id = None
        stop_id = None
        for leg in getattr(order, "legs", None) or ():
            order_type = cls._enum_value(
                getattr(leg, "order_type", None)
                or getattr(leg, "type", "")
            )
            leg_id = cls._optional_id(getattr(leg, "id", None))
            if order_type == "limit":
                target_id = leg_id
            elif order_type in {"stop", "stop_limit"}:
                stop_id = leg_id
        return target_id, stop_id

    @staticmethod
    def _optional_id(value: object) -> str | None:
        normalized = str(value).strip() if value is not None else ""
        return normalized or None

    @staticmethod
    def _enum_value(value: object) -> str:
        return str(getattr(value, "value", value)).strip().lower()
