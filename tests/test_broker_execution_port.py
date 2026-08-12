from imie.execution import BrokerExecutionPort
from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)


class FakeBrokerExecutionAdapter:
    def submit_order(
        self,
        intent: ExecutionOrderIntent,
    ) -> BrokerSubmissionResult:
        return BrokerSubmissionResult(
            broker="fake",
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            accepted=True,
            broker_order_id="fake-123",
            status="accepted",
            message="Fake order accepted.",
        )


def test_adapter_satisfies_broker_execution_port() -> None:
    adapter: BrokerExecutionPort = (
        FakeBrokerExecutionAdapter()
    )

    intent = ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=125,
        order_type="limit",
        entry_price=500.0,
        stop_price=499.0,
        target1_price=501.0,
        target2_price=502.0,
        time_in_force="day",
        valid=True,
        actionable=True,
    )

    result = adapter.submit_order(
        intent
    )

    assert result.broker == "fake"
    assert result.accepted is True
    assert result.symbol == "NVDA"
    assert result.side == "buy"
    assert result.quantity == 125