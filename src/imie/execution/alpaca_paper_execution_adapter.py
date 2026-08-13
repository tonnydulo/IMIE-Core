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
)


class AlpacaTradingClient(Protocol):
    def submit_order(
        self,
        order_data: OrderRequest,
    ) -> object:
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
