from types import SimpleNamespace
from uuid import UUID

import pytest

from alpaca.trading.enums import OrderStatus

from imie.execution import (
    AlpacaPaperExecutionAdapter,
    ProtectedExecutionPlanBuilder,
)
from imie.models import ExecutionOrderIntent


ORDER_1 = UUID("11111111-1111-1111-1111-111111111111")
ORDER_2 = UUID("22222222-2222-2222-2222-222222222222")


class SequencedTradingClient:
    def __init__(
        self,
        outcomes: list[object],
        *,
        cancel_error: Exception | None = None,
    ) -> None:
        self.outcomes = outcomes
        self.cancel_error = cancel_error
        self.requests: list[object] = []
        self.cancelled: list[str] = []

    def submit_order(self, order_data: object) -> object:
        self.requests.append(order_data)
        outcome = self.outcomes[len(self.requests) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def cancel_order_by_id(self, order_id: str) -> None:
        if self.cancel_error is not None:
            raise self.cancel_error
        self.cancelled.append(str(order_id))


def order(order_id: UUID, status: OrderStatus = OrderStatus.ACCEPTED):
    return SimpleNamespace(id=order_id, status=status)


def make_plan(quantity: int = 100):
    intent = ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=quantity,
        order_type="limit",
        entry_price=500.0,
        stop_price=499.0,
        target1_price=501.0,
        target2_price=502.0,
        time_in_force="day",
        valid=True,
        actionable=True,
    )
    return ProtectedExecutionPlanBuilder().build(intent)


def make_adapter(client: object) -> AlpacaPaperExecutionAdapter:
    return AlpacaPaperExecutionAdapter(
        api_key="paper-key",
        secret_key="paper-secret",
        trading_client=client,  # type: ignore[arg-type]
    )


def test_all_brackets_accepted() -> None:
    client = SequencedTradingClient([order(ORDER_1), order(ORDER_2)])
    result = make_adapter(client).submit_protected_plan(make_plan())

    assert result.accepted is True
    assert result.status == "accepted"
    assert tuple(item.broker_order_id for item in result.submissions) == (
        str(ORDER_1),
        str(ORDER_2),
    )
    assert client.cancelled == []


def test_second_rejection_cancels_first_bracket() -> None:
    client = SequencedTradingClient([
        order(ORDER_1),
        order(ORDER_2, OrderStatus.REJECTED),
    ])
    result = make_adapter(client).submit_protected_plan(make_plan())

    assert result.accepted is False
    assert result.status == "rolled_back"
    assert result.rollback_attempted is True
    assert result.rollback_succeeded is True
    assert result.rolled_back_order_ids == (str(ORDER_1),)
    assert client.cancelled == [str(ORDER_1)]


def test_second_error_cancels_first_bracket() -> None:
    client = SequencedTradingClient([
        order(ORDER_1),
        RuntimeError("endpoint unavailable"),
    ])
    result = make_adapter(client).submit_protected_plan(make_plan())

    assert result.status == "rolled_back"
    assert result.submissions[1].status == "error"
    assert "endpoint unavailable" in result.submissions[1].message


def test_cancel_failure_is_visible_and_not_reported_as_safe() -> None:
    client = SequencedTradingClient(
        [order(ORDER_1), order(ORDER_2, OrderStatus.REJECTED)],
        cancel_error=RuntimeError("cancel denied"),
    )
    result = make_adapter(client).submit_protected_plan(make_plan())

    assert result.accepted is False
    assert result.status == "rollback_failed"
    assert result.rollback_succeeded is False
    assert result.rolled_back_order_ids == ()
    assert any("cancel denied" in warning for warning in result.warnings)


def test_first_rejection_does_not_attempt_rollback() -> None:
    client = SequencedTradingClient([
        order(ORDER_1, OrderStatus.REJECTED),
        order(ORDER_2),
    ])
    result = make_adapter(client).submit_protected_plan(make_plan())

    assert result.status == "rejected"
    assert result.rollback_attempted is False
    assert len(client.requests) == 1


def test_single_slice_does_not_require_cancel_support() -> None:
    class SubmitOnlyClient:
        def submit_order(self, order_data: object) -> object:
            return order(ORDER_1)

    result = make_adapter(SubmitOnlyClient()).submit_protected_plan(
        make_plan(quantity=1)
    )

    assert result.accepted is True
    assert len(result.submissions) == 1


def test_multi_slice_requires_cancel_before_any_submission() -> None:
    class SubmitOnlyClient:
        def __init__(self) -> None:
            self.calls = 0

        def submit_order(self, order_data: object) -> object:
            self.calls += 1
            return order(ORDER_1)

    client = SubmitOnlyClient()

    with pytest.raises(TypeError, match="cancel_order_by_id"):
        make_adapter(client).submit_protected_plan(make_plan())

    assert client.calls == 0


def test_invalid_plan_type_raises() -> None:
    adapter = make_adapter(SequencedTradingClient([]))
    with pytest.raises(TypeError, match="ProtectedExecutionPlan"):
        adapter.submit_protected_plan(object())  # type: ignore[arg-type]
