import pytest

from imie.engines.liquidity import EqualLowDetector
from imie.models import (
    LiquidityImportance,
    LiquidityLocation,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    Swing,
)


def make_swing(
    *,
    index: int,
    price: float,
    kind: str,
    strength: int = 3,
) -> Swing:
    return Swing(
        index=index,
        price=price,
        kind=kind,
        strength=strength,
    )


def test_detects_equal_lows() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
        min_separation=2,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
            strength=3,
        ),
        make_swing(
            index=14,
            price=544.94,
            kind="LOW",
            strength=5,
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.liquidity_type is LiquidityType.EQUAL_LOW
    assert finding.point.side is LiquiditySide.SELL_SIDE
    assert finding.point.first_index == 10
    assert finding.point.second_index == 14
    assert finding.point.price == pytest.approx(544.97)
    assert finding.point.strength == 4
    assert finding.importance is LiquidityImportance.MINOR
    assert finding.location is LiquidityLocation.UNCLASSIFIED
    assert finding.state is LiquidityState.ACTIVE
    assert finding.source == "EqualLowDetector"
    assert 0.0 <= finding.confidence <= 100.0


def test_returns_empty_when_fewer_than_two_lows() -> None:
    detector = EqualLowDetector()

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
    )

    assert detector.detect(swings) == ()


def test_ignores_high_swings() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="HIGH",
        ),
        make_swing(
            index=14,
            price=545.05,
            kind="HIGH",
        ),
    )

    assert detector.detect(swings) == ()


def test_rejects_lows_outside_tolerance() -> None:
    detector = EqualLowDetector(
        tolerance=0.05,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=14,
            price=544.94,
            kind="LOW",
        ),
    )

    assert detector.detect(swings) == ()


def test_accepts_lows_at_exact_tolerance() -> None:
    detector = EqualLowDetector(
        tolerance=0.05,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=14,
            price=544.95,
            kind="LOW",
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 1


def test_rejects_lows_below_minimum_separation() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
        min_separation=3,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=12,
            price=544.95,
            kind="LOW",
        ),
    )

    assert detector.detect(swings) == ()


def test_high_swings_between_lows_do_not_block_detection() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=12,
            price=548.00,
            kind="HIGH",
        ),
        make_swing(
            index=15,
            price=544.96,
            kind="LOW",
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 1
    assert findings[0].point.first_index == 10
    assert findings[0].point.second_index == 15


def test_compares_non_adjacent_lows() -> None:
    detector = EqualLowDetector(
        tolerance=0.05,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=14,
            price=543.00,
            kind="LOW",
        ),
        make_swing(
            index=20,
            price=544.97,
            kind="LOW",
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 1
    assert findings[0].point.first_index == 10
    assert findings[0].point.second_index == 20


def test_all_valid_pairs_are_emitted() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    swings = (
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
        make_swing(
            index=14,
            price=544.95,
            kind="LOW",
        ),
        make_swing(
            index=20,
            price=544.92,
            kind="LOW",
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 3

    pairs = {
        (
            finding.point.first_index,
            finding.point.second_index,
        )
        for finding in findings
    }

    assert pairs == {
        (10, 14),
        (10, 20),
        (14, 20),
    }


def test_detector_sorts_swings_by_index() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    swings = (
        make_swing(
            index=20,
            price=544.96,
            kind="LOW",
        ),
        make_swing(
            index=10,
            price=545.00,
            kind="LOW",
        ),
    )

    findings = detector.detect(swings)

    assert len(findings) == 1
    assert findings[0].point.first_index == 10
    assert findings[0].point.second_index == 20


def test_stronger_swings_create_stronger_liquidity_point() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    findings = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
                strength=3,
            ),
            make_swing(
                index=14,
                price=544.98,
                kind="LOW",
                strength=5,
            ),
        )
    )

    assert findings[0].point.strength == 4


def test_more_precise_lows_receive_higher_confidence() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    precise = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
                strength=3,
            ),
            make_swing(
                index=14,
                price=544.99,
                kind="LOW",
                strength=3,
            ),
        )
    )

    marginal = detector.detect(
        (
            make_swing(
                index=20,
                price=545.00,
                kind="LOW",
                strength=3,
            ),
            make_swing(
                index=24,
                price=544.91,
                kind="LOW",
                strength=3,
            ),
        )
    )

    assert precise[0].confidence > marginal[0].confidence


def test_stronger_swings_receive_higher_confidence() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
    )

    weak = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
                strength=1,
            ),
            make_swing(
                index=14,
                price=544.98,
                kind="LOW",
                strength=1,
            ),
        )
    )

    strong = detector.detect(
        (
            make_swing(
                index=20,
                price=545.00,
                kind="LOW",
                strength=5,
            ),
            make_swing(
                index=24,
                price=544.98,
                kind="LOW",
                strength=5,
            ),
        )
    )

    assert strong[0].confidence > weak[0].confidence


def test_better_separation_receives_higher_confidence() -> None:
    detector = EqualLowDetector(
        tolerance=0.10,
        min_separation=2,
        ideal_separation=10,
    )

    close_pair = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
            ),
            make_swing(
                index=12,
                price=544.98,
                kind="LOW",
            ),
        )
    )

    separated_pair = detector.detect(
        (
            make_swing(
                index=20,
                price=545.00,
                kind="LOW",
            ),
            make_swing(
                index=30,
                price=544.98,
                kind="LOW",
            ),
        )
    )

    assert separated_pair[0].confidence > close_pair[0].confidence


def test_exact_matches_work_with_zero_tolerance() -> None:
    detector = EqualLowDetector(
        tolerance=0.0,
    )

    findings = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
            ),
            make_swing(
                index=14,
                price=545.00,
                kind="LOW",
            ),
        )
    )

    assert len(findings) == 1


def test_zero_tolerance_rejects_non_exact_matches() -> None:
    detector = EqualLowDetector(
        tolerance=0.0,
    )

    findings = detector.detect(
        (
            make_swing(
                index=10,
                price=545.00,
                kind="LOW",
            ),
            make_swing(
                index=14,
                price=544.99,
                kind="LOW",
            ),
        )
    )

    assert findings == ()


def test_rejects_negative_tolerance() -> None:
    with pytest.raises(
        ValueError,
        match="tolerance cannot be negative",
    ):
        EqualLowDetector(
            tolerance=-0.01,
        )


def test_rejects_invalid_minimum_separation() -> None:
    with pytest.raises(
        ValueError,
        match="min_separation must be at least 1",
    ):
        EqualLowDetector(
            min_separation=0,
        )


def test_rejects_ideal_separation_below_minimum() -> None:
    with pytest.raises(
        ValueError,
        match="ideal_separation cannot be less",
    ):
        EqualLowDetector(
            min_separation=5,
            ideal_separation=4,
        )