import pytest

from imie.models import BrokerSubmissionResult


def make_result(
    **overrides: object,
) -> BrokerSubmissionResult:
    values = {
        "broker": "mock",
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 125,
        "accepted": True,
        "broker_order_id": "order-123",
        "status": "accepted",
        "message": "Order accepted.",
        "warnings": (),
    }

    values.update(
        overrides
    )

    return BrokerSubmissionResult(
        **values
    )


def test_broker_submission_result_normalizes_values() -> None:
    result = make_result(
        broker=" MOCK ",
        symbol=" nvda ",
        side=" BUY ",
        status=" ACCEPTED ",
        message=" Order accepted. ",
    )

    assert result.broker == "mock"
    assert result.symbol == "NVDA"
    assert result.side == "buy"
    assert result.status == "accepted"
    assert result.message == "Order accepted."


def test_broker_submission_result_allows_rejected_order() -> None:
    result = make_result(
        accepted=False,
        broker_order_id=None,
        status="rejected",
        message="Order rejected.",
    )

    assert result.accepted is False
    assert result.broker_order_id is None
    assert result.status == "rejected"


def test_broker_submission_result_rejects_invalid_side() -> None:
    with pytest.raises(
        ValueError,
        match="side must be buy or sell",
    ):
        make_result(
            side="hold"
        )


def test_broker_submission_result_rejects_negative_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="quantity cannot be negative",
    ):
        make_result(
            quantity=-1
        )


def test_broker_submission_result_cleans_warnings() -> None:
    result = make_result(
        warnings=(
            " warning one ",
            "",
            "warning two",
        )
    )

    assert result.warnings == (
        "warning one",
        "warning two",
    )