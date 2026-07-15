from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    InstitutionalConfluence,
    InstitutionalDirection,
)


def make_directional_confluence(
    *,
    dominant_direction: (
        InstitutionalDirection
    ) = InstitutionalDirection.UNKNOWN,
    bullish_count: int = 0,
    bearish_count: int = 0,
    neutral_count: int = 0,
    unknown_count: int = 3,
    conflict_count: int = 0,
    structure_support: bool = False,
    liquidity_support: bool = False,
    order_block_support: bool = False,
    evidence: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> InstitutionalConfluence:
    agreement_count = sum(
        (
            structure_support,
            liquidity_support,
            order_block_support,
        )
    )

    score = (
        (40.0 if structure_support else 0.0)
        + (30.0 if liquidity_support else 0.0)
        + (30.0 if order_block_support else 0.0)
    )

    adjustment = {
        0: 0.0,
        1: 2.0,
        2: 5.0,
        3: 8.0,
    }[
        agreement_count
    ]

    return InstitutionalConfluence(
        score=score,
        structure_support=structure_support,
        liquidity_support=liquidity_support,
        order_block_support=order_block_support,
        agreement_count=agreement_count,
        confidence_adjustment=adjustment,
        dominant_direction=dominant_direction,
        bullish_count=bullish_count,
        bearish_count=bearish_count,
        neutral_count=neutral_count,
        unknown_count=unknown_count,
        conflict_count=conflict_count,
        evidence=evidence,
        warnings=warnings,
    )


def test_directional_empty_result() -> None:
    result = make_directional_confluence()

    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.bullish_count == 0
    assert result.bearish_count == 0
    assert result.neutral_count == 0
    assert result.unknown_count == 3
    assert result.agreement_count == 0
    assert result.conflict_count == 0


def test_bullish_directional_result() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=3,
        bearish_count=0,
        neutral_count=0,
        unknown_count=0,
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.is_bullish is True
    assert result.is_bearish is False
    assert result.agreement_count == 3
    assert result.conflict_count == 0
    assert result.confidence_bonus == 8.0


def test_bearish_directional_result() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BEARISH
        ),
        bullish_count=0,
        bearish_count=3,
        neutral_count=0,
        unknown_count=0,
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.is_bearish is True
    assert result.is_bullish is False
    assert result.agreement_count == 3
    assert result.conflict_count == 0


def test_bullish_result_with_one_conflict() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=2,
        bearish_count=1,
        neutral_count=0,
        unknown_count=0,
        conflict_count=1,
        structure_support=True,
        liquidity_support=False,
        order_block_support=True,
    )

    assert result.agreement_count == 2
    assert result.conflict_count == 1
    assert result.has_conflict is True
    assert result.is_mixed is True
    assert result.confidence_bonus == 5.0


def test_bearish_result_with_one_conflict() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BEARISH
        ),
        bullish_count=1,
        bearish_count=2,
        neutral_count=0,
        unknown_count=0,
        conflict_count=1,
        structure_support=True,
        liquidity_support=True,
        order_block_support=False,
    )

    assert result.agreement_count == 2
    assert result.conflict_count == 1
    assert result.has_conflict is True
    assert result.is_mixed is True


def test_bullish_with_neutral_domain() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=2,
        bearish_count=0,
        neutral_count=1,
        unknown_count=0,
        structure_support=True,
        liquidity_support=False,
        order_block_support=True,
    )

    assert result.agreement_count == 2
    assert result.conflict_count == 0
    assert result.neutral_count == 1
    assert result.unresolved_count == 1


def test_bearish_with_unknown_domain() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BEARISH
        ),
        bullish_count=0,
        bearish_count=2,
        neutral_count=0,
        unknown_count=1,
        structure_support=True,
        liquidity_support=True,
        order_block_support=False,
    )

    assert result.agreement_count == 2
    assert result.conflict_count == 0
    assert result.unknown_count == 1
    assert result.unresolved_count == 1


def test_all_neutral() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.NEUTRAL
        ),
        bullish_count=0,
        bearish_count=0,
        neutral_count=3,
        unknown_count=0,
    )

    assert result.is_neutral is True
    assert result.agreement_count == 0
    assert result.conflict_count == 0
    assert result.resolved_directional_count == 0


def test_all_unknown() -> None:
    result = make_directional_confluence()

    assert result.is_unknown is True
    assert result.directional_count == 3
    assert result.resolved_directional_count == 0


def test_directional_count() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=1,
        bearish_count=0,
        neutral_count=1,
        unknown_count=1,
        structure_support=True,
    )

    assert result.directional_count == 3


def test_resolved_directional_count() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=1,
        bearish_count=1,
        neutral_count=0,
        unknown_count=1,
        conflict_count=1,
        structure_support=True,
    )

    assert result.resolved_directional_count == 2


def test_unresolved_count() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=1,
        bearish_count=0,
        neutral_count=1,
        unknown_count=1,
        structure_support=True,
    )

    assert result.unresolved_count == 2


def test_has_directional_counts() -> None:
    result = make_directional_confluence()

    assert result.has_directional_counts is True


def test_legacy_result_has_no_directional_counts() -> None:
    result = InstitutionalConfluence(
        score=40.0,
        structure_support=True,
        liquidity_support=False,
        order_block_support=False,
        agreement_count=1,
        confidence_adjustment=2.0,
    )

    assert result.has_directional_counts is False


def test_confidence_bonus_alias() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=2,
        bearish_count=0,
        neutral_count=0,
        unknown_count=1,
        structure_support=True,
        liquidity_support=True,
    )

    assert (
        result.confidence_bonus
        == result.confidence_adjustment
    )
    assert result.confidence_bonus == 5.0


def test_full_agreement_requires_no_conflict() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=3,
        bearish_count=0,
        neutral_count=0,
        unknown_count=0,
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.has_full_agreement is True


def test_partial_agreement() -> None:
    result = make_directional_confluence(
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=2,
        bearish_count=0,
        neutral_count=0,
        unknown_count=1,
        structure_support=True,
        order_block_support=True,
    )

    assert result.has_partial_agreement is True


def test_no_agreement() -> None:
    result = make_directional_confluence()

    assert result.has_no_agreement is True


def test_no_conflict() -> None:
    result = make_directional_confluence()

    assert result.has_conflict is False


def test_direction_alias_is_normalized() -> None:
    result = InstitutionalConfluence(
        score=40.0,
        structure_support=True,
        liquidity_support=False,
        order_block_support=False,
        agreement_count=1,
        confidence_adjustment=2.0,
        dominant_direction="long",  # type: ignore[arg-type]
        bullish_count=1,
        bearish_count=0,
        neutral_count=0,
        unknown_count=2,
        conflict_count=0,
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )


def test_evidence_is_cleaned() -> None:
    result = make_directional_confluence(
        evidence=(
            "",
            "Structure supports bullish continuation.",
            "structure supports bullish continuation.",
            "  Liquidity is neutral.  ",
        ),
    )

    assert result.evidence == (
        "Structure supports bullish continuation.",
        "Liquidity is neutral.",
    )


def test_warnings_are_cleaned() -> None:
    result = make_directional_confluence(
        warnings=(
            "",
            "Institutional conflict detected.",
            "institutional conflict detected.",
        ),
    )

    assert result.warnings == (
        "Institutional conflict detected.",
    )


def test_model_is_frozen() -> None:
    result = make_directional_confluence()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.conflict_count = 2  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "bullish_count",
        "bearish_count",
        "neutral_count",
        "unknown_count",
        "conflict_count",
    ],
)
def test_rejects_negative_directional_counts(
    field_name: str,
) -> None:
    arguments = {
        "bullish_count": 0,
        "bearish_count": 0,
        "neutral_count": 0,
        "unknown_count": 3,
        "conflict_count": 0,
    }

    arguments[
        field_name
    ] = -1

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be between 0 and 3"
        ),
    ):
        make_directional_confluence(
            bullish_count=arguments[
                "bullish_count"
            ],
            bearish_count=arguments[
                "bearish_count"
            ],
            neutral_count=arguments[
                "neutral_count"
            ],
            unknown_count=arguments[
                "unknown_count"
            ],
            conflict_count=arguments[
                "conflict_count"
            ],
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "bullish_count",
        "bearish_count",
        "neutral_count",
        "unknown_count",
        "conflict_count",
    ],
)
def test_rejects_directional_counts_above_three(
    field_name: str,
) -> None:
    arguments = {
        "bullish_count": 0,
        "bearish_count": 0,
        "neutral_count": 0,
        "unknown_count": 3,
        "conflict_count": 0,
    }

    arguments[
        field_name
    ] = 4

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be between 0 and 3"
        ),
    ):
        make_directional_confluence(
            bullish_count=arguments[
                "bullish_count"
            ],
            bearish_count=arguments[
                "bearish_count"
            ],
            neutral_count=arguments[
                "neutral_count"
            ],
            unknown_count=arguments[
                "unknown_count"
            ],
            conflict_count=arguments[
                "conflict_count"
            ],
        )


def test_rejects_directional_total_not_equal_to_three() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Directional counts must total 3"
        ),
    ):
        make_directional_confluence(
            bullish_count=1,
            bearish_count=0,
            neutral_count=0,
            unknown_count=1,
            structure_support=True,
            dominant_direction=(
                InstitutionalDirection.BULLISH
            ),
        )


def test_rejects_bullish_agreement_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bullish dominant direction requires "
            "agreement_count to match bullish_count"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.BULLISH
            ),
            bullish_count=2,
            bearish_count=0,
            neutral_count=0,
            unknown_count=1,
            structure_support=True,
        )


def test_rejects_bullish_conflict_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bullish dominant direction requires "
            "conflict_count to match bearish_count"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.BULLISH
            ),
            bullish_count=1,
            bearish_count=1,
            neutral_count=0,
            unknown_count=1,
            conflict_count=0,
            structure_support=True,
        )


def test_rejects_bearish_agreement_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bearish dominant direction requires "
            "agreement_count to match bearish_count"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.BEARISH
            ),
            bullish_count=0,
            bearish_count=2,
            neutral_count=0,
            unknown_count=1,
            structure_support=True,
        )


def test_rejects_bearish_conflict_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bearish dominant direction requires "
            "conflict_count to match bullish_count"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.BEARISH
            ),
            bullish_count=1,
            bearish_count=1,
            neutral_count=0,
            unknown_count=1,
            conflict_count=0,
            structure_support=True,
        )


def test_rejects_neutral_with_directional_votes() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Neutral dominant direction cannot contain "
            "bullish or bearish directional votes"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.NEUTRAL
            ),
            bullish_count=1,
            bearish_count=0,
            neutral_count=2,
            unknown_count=0,
            structure_support=True,
        )


def test_rejects_unknown_with_agreement() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Unknown dominant direction cannot report "
            "directional agreement"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.UNKNOWN
            ),
            bullish_count=1,
            bearish_count=0,
            neutral_count=0,
            unknown_count=2,
            structure_support=True,
        )


def test_rejects_conflict_above_directional_count() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "conflict_count cannot exceed the number of "
            "directional institutional domains"
        ),
    ):
        make_directional_confluence(
            dominant_direction=(
                InstitutionalDirection.UNKNOWN
            ),
            bullish_count=0,
            bearish_count=0,
            neutral_count=1,
            unknown_count=2,
            conflict_count=1,
        )


def test_rejects_invalid_dominant_direction() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "dominant_direction must be an "
            "InstitutionalDirection"
        ),
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
            dominant_direction="SIDEWAYS",  # type: ignore[arg-type]
        )


def test_directional_empty_factory() -> None:
    result = InstitutionalConfluence.empty(
        directional=True
    )

    assert result.directional_count == 3
    assert result.unknown_count == 3
    assert result.is_unknown is True


def test_legacy_empty_factory() -> None:
    result = InstitutionalConfluence.empty()

    assert result.directional_count == 0
    assert result.has_directional_counts is False