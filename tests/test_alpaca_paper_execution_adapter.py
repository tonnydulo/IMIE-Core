from types import SimpleNamespace
from uuid import UUID

import pytest

from alpaca.trading.enums import (
    OrderSide,
    OrderStatus,
    TimeInForce,
)
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
)

from imie.execution import (
    AlpacaPaperExecutionAdapter,
    BrokerExecutionPort,
)
from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)
import imie.execution.alpaca_paper_execution_adapter as adapter_module


ORDER_ID = UUID(
    "12345678-1234-5678-1234-567812345678"
)


class RecordingTradingClient:
    def __init__(
        self,
        *,
        status: OrderStatus = OrderStatus.ACCEPTED,
        error: Exception | None = None,
    ) -> None:
        self.status = status
        self.error = error
        self.requests: list[object] = []

    def submit_order(
        self,
        order_data: object,
    ) -> object:
        self.requests.append(
            order_data
        )

        if self.error is not None:
            raise self.error

        return SimpleNamespace(
            id=ORDER_ID,
            status=self.status,
        )


def make_intent(
    **overrides: object,
) -> ExecutionOrderIntent:
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 125,
        "order_type": "limit",
        "entry_price": 500.0,
        "stop_price": 499.0,
        "target1_price": 501.0,
        "target2_price": 502.0,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
    }
    values.update(
        overrides
    )
    return ExecutionOrderIntent(
        **values
    )


def make_adapter(
    client: RecordingTradingClient,
) -> AlpacaPaperExecutionAdapter:
    return AlpacaPaperExecutionAdapter(
        api_key="paper-key",
        secret_key="paper-secret",
        trading_client=client,
    )


def test_adapter_satisfies_execution_port() -> None:
    adapter: BrokerExecutionPort = make_adapter(
        RecordingTradingClient()
    )

    result = adapter.submit_order(
        make_intent()
    )

    assert isinstance(
        result,
        BrokerSubmissionResult,
    )


def test_default_client_is_forced_to_paper_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def make_client(
        **arguments: object,
    ) -> RecordingTradingClient:
        captured.update(
            arguments
        )
        return RecordingTradingClient()

    monkeypatch.setattr(
        adapter_module,
        "TradingClient",
        make_client,
    )

    AlpacaPaperExecutionAdapter(
        api_key="paper-key",
        secret_key="paper-secret",
    )

    assert captured == {
        "api_key": "paper-key",
        "secret_key": "paper-secret",
        "paper": True,
    }


def test_limit_intent_is_translated_and_submitted() -> None:
    client = RecordingTradingClient()
    adapter = make_adapter(
        client
    )

    result = adapter.submit_order(
        make_intent()
    )

    assert result.accepted is True
    assert result.broker == "alpaca-paper"
    assert result.broker_order_id == str(
        ORDER_ID
    )
    assert result.status == "accepted"
    assert result.warnings == (
        "Protective stop and profit targets were not "
        "submitted with this entry order.",
    )

    request = client.requests[0]
    assert isinstance(
        request,
        LimitOrderRequest,
    )
    assert request.symbol == "NVDA"
    assert request.qty == 125
    assert request.side is OrderSide.BUY
    assert request.time_in_force is TimeInForce.DAY
    assert request.limit_price == 500.0


def test_market_intent_is_translated_and_submitted() -> None:
    client = RecordingTradingClient()
    adapter = make_adapter(
        client
    )

    result = adapter.submit_order(
        make_intent(
            side="sell",
            order_type="market",
            entry_price=None,
            time_in_force="gtc",
        )
    )

    assert result.accepted is True
    request = client.requests[0]
    assert isinstance(
        request,
        MarketOrderRequest,
    )
    assert request.side is OrderSide.SELL
    assert request.time_in_force is TimeInForce.GTC


def test_non_actionable_intent_is_not_submitted() -> None:
    client = RecordingTradingClient()
    adapter = make_adapter(
        client
    )

    result = adapter.submit_order(
        make_intent(
            actionable=False,
            quantity=0,
        )
    )

    assert result.accepted is False
    assert result.status == "rejected"
    assert client.requests == []


def test_alpaca_rejection_is_reported() -> None:
    adapter = make_adapter(
        RecordingTradingClient(
            status=OrderStatus.REJECTED,
        )
    )

    result = adapter.submit_order(
        make_intent()
    )

    assert result.accepted is False
    assert result.broker_order_id is None
    assert result.status == "rejected"


def test_submission_error_is_reported_without_raising() -> None:
    adapter = make_adapter(
        RecordingTradingClient(
            error=RuntimeError(
                "paper endpoint unavailable"
            ),
        )
    )

    result = adapter.submit_order(
        make_intent()
    )

    assert result.accepted is False
    assert result.status == "rejected"
    assert "paper endpoint unavailable" in result.message


@pytest.mark.parametrize(
    ("name", "value", "exception_type"),
    [
        ("api_key", " ", ValueError),
        ("secret_key", "", ValueError),
        ("api_key", None, TypeError),
        ("secret_key", None, TypeError),
    ],
)
def test_credentials_are_required(
    name: str,
    value: object,
    exception_type: type[Exception],
) -> None:
    arguments = {
        "api_key": "paper-key",
        "secret_key": "paper-secret",
        "trading_client": RecordingTradingClient(),
    }
    arguments[name] = value

    with pytest.raises(
        exception_type,
        match=name,
    ):
        AlpacaPaperExecutionAdapter(
            **arguments,  # type: ignore[arg-type]
        )


def test_trading_client_must_support_submission() -> None:
    with pytest.raises(
        TypeError,
        match="submit_order",
    ):
        AlpacaPaperExecutionAdapter(
            api_key="paper-key",
            secret_key="paper-secret",
            trading_client=object(),  # type: ignore[arg-type]
        )


def test_invalid_intent_type_raises() -> None:
    adapter = make_adapter(
        RecordingTradingClient()
    )

    with pytest.raises(
        TypeError,
        match="ExecutionOrderIntent",
    ):
        adapter.submit_order(
            object()  # type: ignore[arg-type]
        )
