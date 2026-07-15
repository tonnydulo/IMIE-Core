from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)


def create_point() -> LiquidityPoint:
    return LiquidityPoint(
        price=550.25,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        strength=2,
    )


def create_finding() -> LiquidityFinding:
    return LiquidityFinding(
        point=create_point(),
        liquidity_type=LiquidityType.PREVIOUS_DAY_HIGH,
        importance=LiquidityImportance.INTERMEDIATE,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=92.5,
        state=LiquidityState.ACTIVE,
        reason="Previous Day High identified as resting buy-side liquidity.",
        evidence=(
            "Previous Day High detected.",
            "Liquidity remains untouched.",
        ),
        source="PreviousDayDetector",
    )


def test_liquidity_finding_fields() -> None:
    finding = create_finding()

    assert finding.point.price == 550.25
    assert finding.liquidity_type is LiquidityType.PREVIOUS_DAY_HIGH
    assert finding.importance is LiquidityImportance.INTERMEDIATE
    assert finding.location is LiquidityLocation.UNCLASSIFIED
    assert finding.confidence == 92.5
    assert finding.state is LiquidityState.ACTIVE
    assert finding.source == "PreviousDayDetector"


def test_liquidity_finding_is_frozen() -> None:
    finding = create_finding()

    with pytest.raises(FrozenInstanceError):
        finding.confidence = 50.0  # type: ignore[misc]


def test_liquidity_finding_equality() -> None:
    assert create_finding() == create_finding()


def test_is_active_property() -> None:
    assert create_finding().is_active is True


def test_is_major_property() -> None:
    finding = create_finding()

    assert finding.is_major is False

    major = LiquidityFinding(
        point=create_point(),
        liquidity_type=LiquidityType.PREVIOUS_WEEK_HIGH,
        importance=LiquidityImportance.MAJOR,
        location=LiquidityLocation.EXTERNAL,
        confidence=99.0,
        state=LiquidityState.ACTIVE,
        reason="Major liquidity.",
        evidence=("Previous Week High.",),
        source="PreviousWeekDetector",
    )

    assert major.is_major is True


def test_location_helpers() -> None:
    internal = LiquidityFinding(
        point=create_point(),
        liquidity_type=LiquidityType.EQUAL_HIGH,
        importance=LiquidityImportance.MINOR,
        location=LiquidityLocation.INTERNAL,
        confidence=80.0,
        state=LiquidityState.ACTIVE,
        reason="Internal liquidity.",
        evidence=("Equal High.",),
        source="EqualHighDetector",
    )

    assert internal.is_internal is True
    assert internal.is_external is False


@pytest.mark.parametrize(
    ("confidence", "message"),
    [
        (-1.0, "confidence"),
        (101.0, "confidence"),
    ],
)
def test_invalid_confidence(
    confidence: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        LiquidityFinding(
            point=create_point(),
            liquidity_type=LiquidityType.EQUAL_HIGH,
            importance=LiquidityImportance.MINOR,
            location=LiquidityLocation.INTERNAL,
            confidence=confidence,
            state=LiquidityState.ACTIVE,
            reason="Equal High.",
            evidence=("Detected.",),
            source="EqualHighDetector",
        )


def test_reason_cannot_be_empty() -> None:
    with pytest.raises(ValueError, match="reason"):
        LiquidityFinding(
            point=create_point(),
            liquidity_type=LiquidityType.EQUAL_HIGH,
            importance=LiquidityImportance.MINOR,
            location=LiquidityLocation.INTERNAL,
            confidence=80.0,
            state=LiquidityState.ACTIVE,
            reason="",
            evidence=("Detected.",),
            source="EqualHighDetector",
        )


def test_source_cannot_be_empty() -> None:
    with pytest.raises(ValueError, match="source"):
        LiquidityFinding(
            point=create_point(),
            liquidity_type=LiquidityType.EQUAL_HIGH,
            importance=LiquidityImportance.MINOR,
            location=LiquidityLocation.INTERNAL,
            confidence=80.0,
            state=LiquidityState.ACTIVE,
            reason="Equal High.",
            evidence=("Detected.",),
            source="",
        )


def test_evidence_cannot_contain_empty_strings() -> None:
    with pytest.raises(ValueError, match="evidence"):
        LiquidityFinding(
            point=create_point(),
            liquidity_type=LiquidityType.EQUAL_HIGH,
            importance=LiquidityImportance.MINOR,
            location=LiquidityLocation.INTERNAL,
            confidence=80.0,
            state=LiquidityState.ACTIVE,
            reason="Equal High.",
            evidence=("Detected.", ""),
            source="EqualHighDetector",
        )