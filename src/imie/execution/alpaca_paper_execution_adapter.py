from __future__ import annotations

from typing import Protocol

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import (
    OrderSide,
    TimeInForce,
)
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderRequest,
)

from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
    ProtectedExecutionPlan,
    ProtectedOrderSubmission,
    ProtectedPlanSubmissionResult,
)
from imie.execution.alpaca_protected_order_request_builder import (
    AlpacaProtectedOrderRequestBuilder,
)


class AlpacaTradingClient(Protocol):
    def submit_order(
        self,
        order_data: OrderRequest,
    ) -> object:
        ...

    def cancel_order_by_id(
        self,
        order_id: str,
    ) -> None:
        ...


class AlpacaPaperExecutionAdapter:
    """Submit IMIE entry orders to Alpaca's paper endpoint only."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        api_key: str,
        secret_key: str,
        trading_client: AlpacaTradingClient | None = None,
        protected_request_builder: (
            AlpacaProtectedOrderRequestBuilder | None
        ) = None,
    ) -> None:
        self._api_key = self._normalize_credential(
            api_key,
            name="api_key",
        )
        self._secret_key = self._normalize_credential(
            secret_key,
            name="secret_key",
        )

        self._trading_client = (
            trading_client
            if trading_client is not None
            else TradingClient(
                api_key=self._api_key,
                secret_key=self._secret_key,
                paper=True,
            )
        )

        if not callable(
            getattr(
                self._trading_client,
                "submit_order",
                None,
            )
        ):
            raise TypeError(
                "trading_client must expose submit_order()."
            )

        self._protected_request_builder = (
            protected_request_builder
            or AlpacaProtectedOrderRequestBuilder()
        )

        if not isinstance(
            self._protected_request_builder,
            AlpacaProtectedOrderRequestBuilder,
        ):
            raise TypeError(
                "protected_request_builder must be an "
                "AlpacaProtectedOrderRequestBuilder."
            )

    def submit_protected_plan(
        self,
        plan: ProtectedExecutionPlan,
    ) -> ProtectedPlanSubmissionResult:
        if not isinstance(plan, ProtectedExecutionPlan):
            raise TypeError("plan must be a ProtectedExecutionPlan.")

        requests = self._protected_request_builder.build(plan)

        if len(requests) > 1 and not callable(
            getattr(self._trading_client, "cancel_order_by_id", None)
        ):
            raise TypeError(
                "trading_client must expose cancel_order_by_id() "
                "for multi-slice protected plans."
            )

        submissions: list[ProtectedOrderSubmission] = []
        accepted_order_ids: list[str] = []

        for order_slice, request in zip(plan.slices, requests, strict=True):
            try:
                order = self._trading_client.submit_order(order_data=request)
                status = self._enum_value(getattr(order, "status", "unknown"))
                order_id = str(getattr(order, "id", "")).strip() or None
                accepted = order_id is not None and status != "rejected"
                submission = ProtectedOrderSubmission(
                    label=order_slice.label,
                    quantity=order_slice.quantity,
                    accepted=accepted,
                    broker_order_id=order_id if accepted else None,
                    status=status,
                    message=(
                        "Alpaca paper bracket accepted."
                        if accepted
                        else "Alpaca paper bracket rejected."
                    ),
                )
            except Exception as exc:
                submission = ProtectedOrderSubmission(
                    label=order_slice.label,
                    quantity=order_slice.quantity,
                    accepted=False,
                    broker_order_id=None,
                    status="error",
                    message=f"Alpaca paper bracket submission failed: {exc}",
                )

            submissions.append(submission)

            if submission.accepted and submission.broker_order_id is not None:
                accepted_order_ids.append(submission.broker_order_id)
                continue

            return self._rollback_protected_plan(
                plan=plan,
                submissions=tuple(submissions),
                accepted_order_ids=tuple(accepted_order_ids),
            )

        return ProtectedPlanSubmissionResult(
            broker=self.broker_name,
            symbol=plan.symbol,
            side=plan.side,
            quantity=plan.quantity,
            accepted=True,
            status="accepted",
            message="All Alpaca paper brackets were accepted.",
            submissions=tuple(submissions),
            warnings=plan.warnings,
        )

    def _rollback_protected_plan(
        self,
        *,
        plan: ProtectedExecutionPlan,
        submissions: tuple[ProtectedOrderSubmission, ...],
        accepted_order_ids: tuple[str, ...],
    ) -> ProtectedPlanSubmissionResult:
        if not accepted_order_ids:
            return ProtectedPlanSubmissionResult(
                broker=self.broker_name,
                symbol=plan.symbol,
                side=plan.side,
                quantity=plan.quantity,
                accepted=False,
                status="rejected",
                message="Alpaca paper rejected the protected plan.",
                submissions=submissions,
                warnings=plan.warnings,
            )

        rolled_back: list[str] = []
        rollback_warnings: list[str] = []

        for order_id in reversed(accepted_order_ids):
            try:
                self._trading_client.cancel_order_by_id(order_id)
                rolled_back.append(order_id)
            except Exception as exc:
                rollback_warnings.append(
                    f"Failed to cancel Alpaca paper order {order_id}: {exc}"
                )

        rollback_succeeded = len(rolled_back) == len(accepted_order_ids)

        return ProtectedPlanSubmissionResult(
            broker=self.broker_name,
            symbol=plan.symbol,
            side=plan.side,
            quantity=plan.quantity,
            accepted=False,
            status=("rolled_back" if rollback_succeeded else "rollback_failed"),
            message=(
                "Partial protected submission was fully rolled back."
                if rollback_succeeded
                else "Partial protected submission could not be fully rolled back."
            ),
            submissions=submissions,
            rollback_attempted=True,
            rollback_succeeded=rollback_succeeded,
            rolled_back_order_ids=tuple(rolled_back),
            warnings=plan.warnings + tuple(rollback_warnings),
        )

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
            return self._rejected_result(
                intent=intent,
                message=(
                    "Execution order intent is not actionable."
                ),
            )

        try:
            request = self._build_order_request(
                intent
            )
            order = self._trading_client.submit_order(
                order_data=request
            )
        except Exception as exc:
            return self._rejected_result(
                intent=intent,
                message=(
                    "Alpaca paper order submission failed: "
                    f"{exc}"
                ),
            )

        status = self._enum_value(
            getattr(
                order,
                "status",
                "unknown",
            )
        )
        broker_order_id = str(
            getattr(
                order,
                "id",
                "",
            )
        ).strip() or None
        accepted = (
            broker_order_id is not None
            and status != "rejected"
        )

        return BrokerSubmissionResult(
            broker=self.broker_name,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            accepted=accepted,
            broker_order_id=(
                broker_order_id
                if accepted
                else None
            ),
            status=status,
            message=(
                "Alpaca paper entry order submitted."
                if accepted
                else "Alpaca paper order was rejected."
            ),
            warnings=(
                "Protective stop and profit targets were not "
                "submitted with this entry order.",
            ),
        )

    @staticmethod
    def _normalize_credential(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        credential = value.strip()

        if not credential:
            raise ValueError(
                f"{name} cannot be empty."
            )

        return credential

    @staticmethod
    def _build_order_request(
        intent: ExecutionOrderIntent,
    ) -> OrderRequest:
        common = {
            "symbol": intent.symbol,
            "qty": intent.quantity,
            "side": OrderSide(intent.side),
            "time_in_force": TimeInForce(
                intent.time_in_force
            ),
        }

        if intent.order_type == "market":
            return MarketOrderRequest(
                **common
            )

        if intent.entry_price is None:
            raise ValueError(
                "A limit order requires entry_price."
            )

        return LimitOrderRequest(
            **common,
            limit_price=intent.entry_price,
        )

    @classmethod
    def _rejected_result(
        cls,
        *,
        intent: ExecutionOrderIntent,
        message: str,
    ) -> BrokerSubmissionResult:
        return BrokerSubmissionResult(
            broker=cls.broker_name,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            accepted=False,
            broker_order_id=None,
            status="rejected",
            message=message,
            warnings=(
                "Alpaca paper broker did not accept the order.",
            ),
        )

    @staticmethod
    def _enum_value(
        value: object,
    ) -> str:
        normalized = getattr(
            value,
            "value",
            value,
        )
        return str(
            normalized
        ).strip().lower() or "unknown"
