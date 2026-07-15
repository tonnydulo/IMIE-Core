from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    OrderBlock,
    OrderBlockFinding,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockState,
)


def make_finding(
    *,
    upper: float = 550.00,
    lower: float = 549.50,
    side: OrderBlockSide = OrderBlockSide.BULLISH,
    origin: OrderBlockOrigin = OrderBlockOrigin.BOS,
    source_bar_index: int = 10,
    displacement: float = 1.25,
    strength: float = 85.0,
    confidence: float = 92.0,
    reason: str = (
        "A bearish source candle preceded confirmed "
        "bullish displacement."
    ),
    evidence: tuple[str, ...] = (
        "The source candle closed bearish.",
        "Subsequent price action displaced upward.",
        "A bullish break of structure was confirmed.",
    ),
    detector: str = "BullishOrderBlockDetector",
) -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=upper,
        lower=lower,
        side=side,
        origin=origin,
        source_bar_index=source_bar_index,
        displacement=displacement,
        strength=strength,
        confidence=confidence,
        reason=reason,
        evidence=evidence,
        detector=detector,
    )


def test_order_block_finding_fields() -> None:
    finding = make_finding()

    assert finding.upper == 550.00
    assert finding.lower == 549.50
    assert finding.side is OrderBlockSide.BULLISH
    assert finding.origin is OrderBlockOrigin.BOS
    assert finding.source_bar_index == 10
    assert finding.displacement == 1.25
    assert finding.strength == 85.0
    assert finding.confidence == 92.0
    assert finding.detector == "BullishOrderBlockDetector"


def test_order_block_finding_is_frozen() -> None:
    finding = make_finding()

    with pytest.raises(FrozenInstanceError):
        finding.confidence = 50.0  # type: ignore[misc]


def test_midpoint() -> None:
    finding = make_finding(
        upper=550.00,
        lower=549.50,
    )

    assert finding.midpoint == pytest.approx(549.75)


def test_height() -> None:
    finding = make_finding(
        upper=550.00,
        lower=549.50,
    )

    assert finding.height == pytest.approx(0.50)


def test_bullish_helper() -> None:
    finding = make_finding(
        side=OrderBlockSide.BULLISH,
    )

    assert finding.is_bullish is True
    assert finding.is_bearish is False


def test_bearish_helper() -> None:
    finding = make_finding(
        side=OrderBlockSide.BEARISH,
        detector="BearishOrderBlockDetector",
    )

    assert finding.is_bearish is True
    assert finding.is_bullish is False


def test_allows_zero_height_finding() -> None:
    finding = make_finding(
        upper=550.00,
        lower=550.00,
    )

    assert finding.height == 0.0
    assert finding.midpoint == 550.00


def test_allows_zero_displacement() -> None:
    finding = make_finding(
        displacement=0.0,
    )

    assert finding.displacement == 0.0


def test_allows_zero_strength() -> None:
    finding = make_finding(
        strength=0.0,
    )

    assert finding.strength == 0.0


@pytest.mark.parametrize(
    "confidence",
    [
        0.0,
        100.0,
    ],
)
def test_accepts_confidence_boundaries(
    confidence: float,
) -> None:
    finding = make_finding(
        confidence=confidence,
    )

    assert finding.confidence == confidence


def test_promotes_to_order_block() -> None:
    finding = make_finding()

    block = finding.to_order_block()

    assert isinstance(block, OrderBlock)


def test_promoted_block_retains_price_range() -> None:
    finding = make_finding(
        upper=550.25,
        lower=549.75,
    )

    block = finding.to_order_block()

    assert block.upper == 550.25
    assert block.lower == 549.75


def test_promoted_block_retains_side() -> None:
    finding = make_finding(
        side=OrderBlockSide.BEARISH,
    )

    block = finding.to_order_block()

    assert block.side is OrderBlockSide.BEARISH


def test_promoted_block_retains_origin() -> None:
    finding = make_finding(
        origin=OrderBlockOrigin.MSS,
    )

    block = finding.to_order_block()

    assert block.origin is OrderBlockOrigin.MSS


def test_promoted_block_is_active() -> None:
    finding = make_finding()

    block = finding.to_order_block()

    assert block.state is OrderBlockState.ACTIVE
    assert block.is_active is True


def test_promoted_block_retains_source_index() -> None:
    finding = make_finding(
        source_bar_index=25,
    )

    block = finding.to_order_block()

    assert block.source_bar_index == 25


def test_promoted_block_uses_source_as_creation_index() -> None:
    finding = make_finding(
        source_bar_index=25,
    )

    block = finding.to_order_block()

    assert block.created_bar_index == 25


def test_promoted_block_retains_strength() -> None:
    finding = make_finding(
        strength=74.0,
    )

    block = finding.to_order_block()

    assert block.strength == 74.0


def test_promoted_block_retains_confidence() -> None:
    finding = make_finding(
        confidence=88.0,
    )

    block = finding.to_order_block()

    assert block.confidence == 88.0


def test_promoted_block_retains_reason() -> None:
    finding = make_finding(
        reason="Confirmed institutional displacement.",
    )

    block = finding.to_order_block()

    assert (
        block.reason
        == "Confirmed institutional displacement."
    )


def test_promoted_block_retains_evidence() -> None:
    evidence = (
        "Source candle identified.",
        "Displacement confirmed.",
    )

    finding = make_finding(
        evidence=evidence,
    )

    block = finding.to_order_block()

    assert block.evidence == evidence


def test_promoted_block_has_no_warnings() -> None:
    finding = make_finding()

    block = finding.to_order_block()

    assert block.warnings == ()


def test_rejects_invalid_side_type() -> None:
    with pytest.raises(
        TypeError,
        match="side must be an OrderBlockSide",
    ):
        make_finding(
            side="BULLISH",  # type: ignore[arg-type]
        )


def test_rejects_invalid_origin_type() -> None:
    with pytest.raises(
        TypeError,
        match="origin must be an OrderBlockOrigin",
    ):
        make_finding(
            origin="BOS",  # type: ignore[arg-type]
        )


def test_rejects_upper_below_lower() -> None:
    with pytest.raises(
        ValueError,
        match="upper cannot be below lower",
    ):
        make_finding(
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
        make_finding(
            upper=upper,
            lower=lower,
        )


def test_rejects_negative_source_bar_index() -> None:
    with pytest.raises(
        ValueError,
        match="source_bar_index cannot be negative",
    ):
        make_finding(
            source_bar_index=-1,
        )


def test_rejects_negative_displacement() -> None:
    with pytest.raises(
        ValueError,
        match="displacement cannot be negative",
    ):
        make_finding(
            displacement=-0.01,
        )


def test_rejects_negative_strength() -> None:
    with pytest.raises(
        ValueError,
        match="strength cannot be negative",
    ):
        make_finding(
            strength=-0.01,
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
        make_finding(
            confidence=confidence,
        )


def test_rejects_empty_reason() -> None:
    with pytest.raises(
        ValueError,
        match="reason cannot be empty",
    ):
        make_finding(
            reason="",
        )


def test_rejects_whitespace_only_reason() -> None:
    with pytest.raises(
        ValueError,
        match="reason cannot be empty",
    ):
        make_finding(
            reason="   ",
        )


def test_rejects_empty_detector() -> None:
    with pytest.raises(
        ValueError,
        match="detector cannot be empty",
    ):
        make_finding(
            detector="",
        )


def test_rejects_whitespace_only_detector() -> None:
    with pytest.raises(
        ValueError,
        match="detector cannot be empty",
    ):
        make_finding(
            detector="   ",
        )


def test_rejects_empty_evidence_entry() -> None:
    with pytest.raises(
        ValueError,
        match="evidence entries cannot be empty",
    ):
        make_finding(
            evidence=(
                "Valid evidence.",
                "",
            ),
        )


def test_rejects_whitespace_only_evidence_entry() -> None:
    with pytest.raises(
        ValueError,
        match="evidence entries cannot be empty",
    ):
        make_finding(
            evidence=(
                "Valid evidence.",
                "   ",
            ),
        )