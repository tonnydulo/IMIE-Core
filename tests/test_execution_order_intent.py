import pytest

from imie.models import ExecutionOrderIntent


def make_intent(
    **overrides: object,
) -> ExecutionOrderIntent:
    values: dict[str, object] = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 100,
        "order_type": "limit",
        "entry_price": 500.00,
        "stop_price": 499.00,
        "target1_price": 501.00,
        "target2_price": 502.00,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
        "reasons": (
            "Execution candidate approved.",
        ),
        "warnings": (),
    }

    values.update(
        overrides
    )

    return ExecutionOrderIntent(
        **values,  # type: ignore[arg-type]
    )


def test_execution_order_intent_can_be_created() -> None:
    intent = make_intent()

    assert intent.symbol == "NVDA"
    assert intent.side == "buy"
    assert intent.quantity == 100
    assert intent.order_type == "limit"
    assert intent.entry_price == 500.00
    assert intent.stop_price == 499.00
    assert intent.target1_price == 501.00
    assert intent.target2_price == 502.00
    assert intent.time_in_force == "day"
    assert intent.valid is True
    assert intent.actionable is True


def test_symbol_and_text_fields_are_normalized() -> None:
    intent = make_intent(
        symbol=" nvda ",
        side=" BUY ",
        order_type=" LIMIT ",
        time_in_force=" DAY ",
    )

    assert intent.symbol == "NVDA"
    assert intent.side == "buy"
    assert intent.order_type == "limit"
    assert intent.time_in_force == "day"


@pytest.mark.parametrize(
    "side",
    (
        "",
        "long",
        "short",
        "hold",
    ),
)
def test_invalid_side_is_rejected(
    side: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="side",
    ):
        make_intent(
            side=side
        )


@pytest.mark.parametrize(
    "order_type",
    (
        "",
        "stop",
        "bracket",
    ),
)
def test_invalid_order_type_is_rejected(
    order_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="order_type",
    ):
        make_intent(
            order_type=order_type
        )


def test_negative_quantity_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="quantity",
    ):
        make_intent(
            quantity=-1
        )


def test_actionable_intent_requires_positive_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="positive quantity",
    ):
        make_intent(
            quantity=0,
            actionable=True,
        )


def test_non_actionable_intent_can_have_zero_quantity() -> None:
    intent = make_intent(
        quantity=0,
        actionable=False,
    )

    assert intent.quantity == 0
    assert intent.actionable is False


@pytest.mark.parametrize(
    "field_name",
    (
        "stop_price",
        "target1_price",
        "target2_price",
    ),
)
def test_required_prices_must_be_positive(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        make_intent(
            **{
                field_name: 0.0,
            }
        )


def test_limit_order_accepts_entry_price() -> None:
    intent = make_intent(
        order_type="limit",
        entry_price=500.25,
    )

    assert intent.entry_price == 500.25


def test_market_order_can_omit_entry_price() -> None:
    intent = make_intent(
        order_type="market",
        entry_price=None,
    )

    assert intent.entry_price is None