import json

import pytest

from imie.execution import (
    ConsoleReconciliationResultPublisher,
    JsonReconciliationResultPublisher,
)
from imie.models import (
    BrokerOrderStatus,
    ExecutionReconciliationResult,
)


def result(
    *,
    reconciled: bool = True,
) -> ExecutionReconciliationResult:
    return ExecutionReconciliationResult(
        broker="alpaca-paper",
        broker_order_id="order-123",
        symbol="NVDA",
        side="buy",
        status=BrokerOrderStatus.PARTIALLY_FILLED,
        intent_quantity=100,
        broker_requested_quantity=100,
        broker_filled_quantity=40,
        recorded_fill_quantity=40 if reconciled else 25,
        broker_average_fill_price=201.25,
        recorded_average_fill_price=201.25 if reconciled else 201.0,
        identity_matched=True,
        quantity_matched=True,
        fills_matched=reconciled,
        reconciled=reconciled,
        discrepancies=(
            ()
            if reconciled
            else ("Recorded fill quantity does not match broker truth.",)
        ),
        warnings=("Broker update may be delayed.",),
    )


def test_json_publisher_serializes_stable_payload() -> None:
    publisher = JsonReconciliationResultPublisher(sort_keys=False)

    payload = publisher.to_dict(result())

    assert payload == {
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "symbol": "NVDA",
        "side": "buy",
        "status": "partially_filled",
        "intent_quantity": 100,
        "broker_requested_quantity": 100,
        "broker_filled_quantity": 40,
        "recorded_fill_quantity": 40,
        "broker_average_fill_price": 201.25,
        "recorded_average_fill_price": 201.25,
        "identity_matched": True,
        "quantity_matched": True,
        "fills_matched": True,
        "reconciled": True,
        "discrepancies": [],
        "warnings": ["Broker update may be delayed."],
    }


def test_json_publish_emits_one_document() -> None:
    output: list[str] = []
    publisher = JsonReconciliationResultPublisher(
        output=output.append,
        indent=2,
    )

    publisher.publish(result(reconciled=False))

    assert len(output) == 1
    payload = json.loads(output[0])
    assert payload["reconciled"] is False
    assert payload["discrepancies"] == [
        "Recorded fill quantity does not match broker truth."
    ]


def test_console_publisher_formats_reconciled_result() -> None:
    lines = ConsoleReconciliationResultPublisher.format_lines(result())

    assert "IMIE Execution Reconciliation" in lines
    assert "Broker Status       : partially_filled" in lines
    assert "Broker Avg Fill     : $201.2500" in lines
    assert "Reconciled          : True" in lines
    assert "Discrepancies       :" not in lines
    assert "Warnings            :" in lines


def test_console_publisher_renders_discrepancies() -> None:
    output: list[str] = []
    ConsoleReconciliationResultPublisher(
        output=output.append
    ).publish(result(reconciled=False))

    assert "Reconciled          : False" in output
    assert "Discrepancies       :" in output
    assert (
        " - Recorded fill quantity does not match broker truth."
        in output
    )


def test_console_renders_missing_prices_as_not_available() -> None:
    no_fill = ExecutionReconciliationResult(
        broker="alpaca-paper",
        broker_order_id="order-123",
        symbol="NVDA",
        side="buy",
        status=BrokerOrderStatus.ACCEPTED,
        intent_quantity=100,
        broker_requested_quantity=100,
        broker_filled_quantity=0,
        recorded_fill_quantity=0,
        broker_average_fill_price=None,
        recorded_average_fill_price=None,
        identity_matched=True,
        quantity_matched=True,
        fills_matched=True,
        reconciled=True,
    )

    lines = ConsoleReconciliationResultPublisher.format_lines(no_fill)

    assert "Broker Avg Fill     : n/a" in lines
    assert "Recorded Avg Fill   : n/a" in lines


@pytest.mark.parametrize(
    "publisher",
    [
        JsonReconciliationResultPublisher(),
        ConsoleReconciliationResultPublisher(),
    ],
)
def test_publishers_reject_other_result_types(publisher: object) -> None:
    with pytest.raises(TypeError, match="ExecutionReconciliationResult"):
        publisher.publish(object())  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("arguments", "exception"),
    [
        ({"output": None}, TypeError),
        ({"indent": True}, TypeError),
        ({"indent": -1}, ValueError),
        ({"sort_keys": "yes"}, TypeError),
    ],
)
def test_json_publisher_configuration_validation(
    arguments: dict[str, object],
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        JsonReconciliationResultPublisher(**arguments)

