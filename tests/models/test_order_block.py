from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    OrderBlock,
    OrderBlockImportance,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockState,
)


def make_order_block(
    *,
    upper: float = 550.00,
    lower: float = 549.50,
    side: OrderBlockSide = OrderBlockSide.BULLISH,
    origin: OrderBlockOrigin = OrderBlockOrigin.BOS,
    state: OrderBlockState = OrderBlockState.ACTIVE,
    source_bar_index: int = 10,
    created_bar_index: int = 14,
    strength: float = 85.0,
    confidence: float = 92.0,
    reason: str = "Bullish order block confirmed after BOS.",
    evidence: tuple[str, ...] = (
        "A bearish source candle preceded bullish displacement.",
        "Completed price action confirmed a bullish BOS.",
    ),
    warnings: tuple[str, ...] = (),
) -> OrderBlock:
    return OrderBlock(
        upper=upper,
        lower=lower,
        side=side,
        origin=origin,
        state=state,
        source_bar_index=source_bar_index,
        created_bar_index=created_bar_index,
        strength=strength,
        confidence=confidence,
        reason=reason,
        evidence=evidence,
        warnings=warnings,
    )


def test_order_block_fields() -> None:
    block = make_order_block()

    assert block.upper == 550.00
    assert block.lower == 549.50
    assert block.side is OrderBlockSide.BULLISH
    assert block.origin is OrderBlockOrigin.BOS
    assert block.state is OrderBlockState.ACTIVE
    assert block.source_bar_index == 10
    assert block.created_bar_index == 14
    assert block.strength == 85.0
    assert block.confidence == 92.0


def test_order_block_is_frozen() -> None:
    block = make_order_block()

    with pytest.raises(FrozenInstanceError):
        block.confidence = 50.0  # type: ignore[misc]


def test_midpoint() -> None:
    block = make_order_block(
        upper=550.00,
        lower=549.50,
    )

    assert block.midpoint == pytest.approx(549.75)


def test_height() -> None:
    block = make_order_block(
        upper=550.00,
        lower=549.50,
    )

    assert block.height == pytest.approx(0.50)


def test_bullish_helper() -> None:
    block = make_order_block(
        side=OrderBlockSide.BULLISH,
    )

    assert block.is_bullish is True
    assert block.is_bearish is False


def test_bearish_helper() -> None:
    block = make_order_block(
        side=OrderBlockSide.BEARISH,
    )

    assert block.is_bearish is True
    assert block.is_bullish is False


@pytest.mark.parametrize(
    (
        "state",
        "property_name",
    ),
    [
        (
            OrderBlockState.ACTIVE,
            "is_active",
        ),
        (
            OrderBlockState.TESTED,
            "is_tested",
        ),
        (
            OrderBlockState.MITIGATED,
            "is_mitigated",
        ),
        (
            OrderBlockState.BROKEN,
            "is_broken",
        ),
        (
            OrderBlockState.RETIRED,
            "is_retired",
        ),
    ],
)
def test_state_helpers(
    state: OrderBlockState,
    property_name: str,
) -> None:
    block = make_order_block(
        state=state,
    )

    assert getattr(block, property_name) is True


@pytest.mark.parametrize(
    (
        "strength",
        "expected",
    ),
    [
        (
            0.0,
            OrderBlockImportance.MINOR,
        ),
        (
            49.99,
            OrderBlockImportance.MINOR,
        ),
        (
            50.0,
            OrderBlockImportance.INTERMEDIATE,
        ),
        (
            79.99,
            OrderBlockImportance.INTERMEDIATE,
        ),
        (
            80.0,
            OrderBlockImportance.MAJOR,
        ),
        (
            100.0,
            OrderBlockImportance.MAJOR,
        ),
    ],
)
def test_importance_is_derived_from_strength(
    strength: float,
    expected: OrderBlockImportance,
) -> None:
    block = make_order_block(
        strength=strength,
    )

    assert block.importance is expected


def test_major_helper() -> None:
    block = make_order_block(
        strength=85.0,
    )

    assert block.is_major is True


def test_non_major_helper() -> None:
    block = make_order_block(
        strength=60.0,
    )

    assert block.is_major is False


def test_allows_zero_height_block() -> None:
    block = make_order_block(
        upper=550.00,
        lower=550.00,
    )

    assert block.height == 0.0


def test_rejects_upper_below_lower() -> None:
    with pytest.raises(
        ValueError,
        match="upper cannot be below lower",
    ):
        make_order_block(
            upper=549.00,
            lower=550.00,
        )


@pytest.mark.parametrize(
    (
        "upper",
        "lower",
    ),
    [
        (
            0.0,
            549.50,
        ),
        (
            -1.0,
            549.50,
        ),
        (
            550.00,
            0.0,
        ),
        (
            550.00,
            -1.0,
        ),
    ],
)
def test_rejects_non_positive_prices(
    upper: float,
    lower: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="must be positive",
    ):
        make_order_block(
            upper=upper,
            lower=lower,
        )


def test_rejects_negative_source_bar_index() -> None:
    with pytest.raises(
        ValueError,
        match="source_bar_index cannot be negative",
    ):
        make_order_block(
            source_bar_index=-1,
        )


def test_rejects_creation_before_source() -> None:
    with pytest.raises(
        ValueError,
        match="created_bar_index cannot be earlier",
    ):
        make_order_block(
            source_bar_index=10,
            created_bar_index=9,
        )


def test_rejects_negative_strength() -> None:
    with pytest.raises(
        ValueError,
        match="strength cannot be negative",
    ):
        make_order_block(
            strength=-1.0,
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -1.0,
        101.0,
    ],
)
def test_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 100",
    ):
        make_order_block(
            confidence=confidence,
        )


def test_rejects_invalid_side_type() -> None:
    with pytest.raises(
        TypeError,
        match="side must be an OrderBlockSide",
    ):
        make_order_block(
            side="BULLISH",  # type: ignore[arg-type]
        )


def test_rejects_invalid_origin_type() -> None:
    with pytest.raises(
        TypeError,
        match="origin must be an OrderBlockOrigin",
    ):
        make_order_block(
            origin="BOS",  # type: ignore[arg-type]
        )


def test_rejects_invalid_state_type() -> None:
    with pytest.raises(
        TypeError,
        match="state must be an OrderBlockState",
    ):
        make_order_block(
            state="ACTIVE",  # type: ignore[arg-type]
        )


def test_rejects_empty_reason() -> None:
    with pytest.raises(
        ValueError,
        match="reason cannot be empty",
    ):
        make_order_block(
            reason="",
        )


def test_rejects_empty_evidence_entry() -> None:
    with pytest.raises(
        ValueError,
        match="evidence entries must be non-empty strings",
    ):
        make_order_block(
            evidence=("Valid evidence.", ""),
        )


def test_rejects_empty_warning_entry() -> None:
    with pytest.raises(
        ValueError,
        match="warning entries must be non-empty strings",
    ):
        make_order_block(
            warnings=("",),
        )