from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    InstitutionalBias,
    InstitutionalDirection,
)


def make_bias(
    *,
    direction: InstitutionalDirection = (
        InstitutionalDirection.BULLISH
    ),
    confidence: float = 90.0,
    bullish_score: float = 70.0,
    bearish_score: float = 20.0,
    agreement_count: int = 2,
    conflict_count: int = 1,
    supporting_domains: tuple[str, ...] = (
        "TREND",
        "STRUCTURE",
    ),
    opposing_domains: tuple[str, ...] = (
        "LIQUIDITY",
    ),
    neutral_domains: tuple[str, ...] = (
        "VALUE",
    ),
    unknown_domains: tuple[str, ...] = (
        "AUCTION",
    ),
    evidence: tuple[str, ...] = (
        "Trend supports bullish continuation.",
    ),
    warnings: tuple[str, ...] = (
        "Liquidity opposes the dominant bias.",
    ),
) -> InstitutionalBias:
    return InstitutionalBias(
        direction=direction,
        strength=round(
            abs(
                bullish_score
                - bearish_score
            ),
            2,
        ),
        confidence=confidence,
        bullish_score=bullish_score,
        bearish_score=bearish_score,
        agreement_count=agreement_count,
        conflict_count=conflict_count,
        supporting_domains=supporting_domains,
        opposing_domains=opposing_domains,
        neutral_domains=neutral_domains,
        unknown_domains=unknown_domains,
        evidence=evidence,
        warnings=warnings,
    )


def test_constructs_institutional_bias() -> None:
    result = make_bias()

    assert isinstance(
        result,
        InstitutionalBias,
    )


def test_fields_are_stored() -> None:
    result = make_bias()

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.strength == 50.0
    assert result.confidence == 90.0
    assert result.bullish_score == 70.0
    assert result.bearish_score == 20.0
    assert result.agreement_count == 2
    assert result.conflict_count == 1


def test_bullish_helper() -> None:
    result = make_bias()

    assert result.is_bullish is True
    assert result.is_bearish is False


def test_bearish_helper() -> None:
    result = make_bias(
        direction=InstitutionalDirection.BEARISH,
        bullish_score=20.0,
        bearish_score=70.0,
        supporting_domains=(
            "TREND",
            "STRUCTURE",
        ),
        opposing_domains=(
            "LIQUIDITY",
        ),
    )

    assert result.is_bearish is True
    assert result.is_bullish is False


def test_neutral_helper() -> None:
    result = make_bias(
        direction=InstitutionalDirection.NEUTRAL,
        bullish_score=40.0,
        bearish_score=40.0,
        agreement_count=0,
        conflict_count=0,
        supporting_domains=(),
        opposing_domains=(),
        neutral_domains=(
            "TREND",
            "STRUCTURE",
        ),
    )

    assert result.is_neutral is True
    assert result.is_directional is False


def test_unknown_helper() -> None:
    result = make_bias(
        direction=InstitutionalDirection.UNKNOWN,
        confidence=0.0,
        bullish_score=0.0,
        bearish_score=0.0,
        agreement_count=0,
        conflict_count=0,
        supporting_domains=(),
        opposing_domains=(),
        neutral_domains=(),
        unknown_domains=(
            "TREND",
            "STRUCTURE",
        ),
        evidence=(),
        warnings=(),
    )

    assert result.is_unknown is True
    assert result.is_directional is False


def test_has_agreement() -> None:
    result = make_bias()

    assert result.has_agreement is True


def test_has_conflict() -> None:
    result = make_bias()

    assert result.has_conflict is True


def test_is_mixed() -> None:
    result = make_bias()

    assert result.is_mixed is True


def test_no_conflict_is_not_mixed() -> None:
    result = make_bias(
        agreement_count=3,
        conflict_count=0,
        supporting_domains=(
            "TREND",
            "STRUCTURE",
            "LIQUIDITY",
        ),
        opposing_domains=(),
    )

    assert result.has_conflict is False
    assert result.is_mixed is False


def test_classified_domain_count() -> None:
    result = make_bias()

    assert result.classified_domain_count == 5


def test_directional_domain_count() -> None:
    result = make_bias()

    assert result.directional_domain_count == 3


def test_unresolved_domain_count() -> None:
    result = make_bias()

    assert result.unresolved_domain_count == 2


def test_score_spread_alias() -> None:
    result = make_bias()

    assert result.score_spread == 50.0


def test_domains_are_normalized() -> None:
    result = make_bias(
        supporting_domains=(
            " trend ",
            "Structure",
        ),
        opposing_domains=(
            "liquidity",
        ),
        neutral_domains=(
            "Value",
        ),
        unknown_domains=(
            "auction",
        ),
    )

    assert result.supporting_domains == (
        "TREND",
        "STRUCTURE",
    )
    assert result.opposing_domains == (
        "LIQUIDITY",
    )
    assert result.neutral_domains == (
        "VALUE",
    )
    assert result.unknown_domains == (
        "AUCTION",
    )


def test_duplicate_domains_are_removed() -> None:
    result = make_bias(
        agreement_count=2,
        supporting_domains=(
            "TREND",
            "trend",
            "STRUCTURE",
            "structure",
        ),
    )

    assert result.supporting_domains == (
        "TREND",
        "STRUCTURE",
    )


def test_evidence_is_cleaned() -> None:
    result = make_bias(
        evidence=(
            "",
            "Trend supports bullish continuation.",
            "trend supports bullish continuation.",
            "  Structure supports bullish continuation.  ",
        ),
    )

    assert result.evidence == (
        "Trend supports bullish continuation.",
        "Structure supports bullish continuation.",
    )


def test_warnings_are_cleaned() -> None:
    result = make_bias(
        warnings=(
            "",
            "Liquidity opposes the dominant bias.",
            "liquidity opposes the dominant bias.",
        ),
    )

    assert result.warnings == (
        "Liquidity opposes the dominant bias.",
    )


def test_direction_alias_is_normalized() -> None:
    result = InstitutionalBias(
        direction="long",  # type: ignore[arg-type]
        strength=50.0,
        confidence=90.0,
        bullish_score=70.0,
        bearish_score=20.0,
        agreement_count=2,
        conflict_count=1,
        supporting_domains=(
            "TREND",
            "STRUCTURE",
        ),
        opposing_domains=(
            "LIQUIDITY",
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )


def test_numeric_values_are_rounded() -> None:
    result = InstitutionalBias(
        direction=InstitutionalDirection.BULLISH,
        strength=50.004,
        confidence=89.996,
        bullish_score=70.004,
        bearish_score=20.0,
        agreement_count=1,
        conflict_count=0,
        supporting_domains=(
            "TREND",
        ),
    )

    assert result.strength == 50.0
    assert result.confidence == 90.0
    assert result.bullish_score == 70.0


def test_model_is_frozen() -> None:
    result = make_bias()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.confidence = 50.0  # type: ignore[misc]


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "strength",
            -0.01,
        ),
        (
            "strength",
            100.01,
        ),
        (
            "confidence",
            -0.01,
        ),
        (
            "confidence",
            100.01,
        ),
        (
            "bullish_score",
            -0.01,
        ),
        (
            "bullish_score",
            100.01,
        ),
        (
            "bearish_score",
            -0.01,
        ),
        (
            "bearish_score",
            100.01,
        ),
    ],
)
def test_rejects_values_outside_range(
    field_name: str,
    value: float,
) -> None:
    arguments = {
        "direction": InstitutionalDirection.BULLISH,
        "strength": 50.0,
        "confidence": 90.0,
        "bullish_score": 70.0,
        "bearish_score": 20.0,
        "agreement_count": 2,
        "conflict_count": 1,
        "supporting_domains": (
            "TREND",
            "STRUCTURE",
        ),
        "opposing_domains": (
            "LIQUIDITY",
        ),
    }

    arguments[
        field_name
    ] = value

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be between 0 and 100"
        ),
    ):
        InstitutionalBias(
            **arguments,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "agreement_count",
        "conflict_count",
    ],
)
def test_rejects_negative_counts(
    field_name: str,
) -> None:
    arguments = {
        "direction": InstitutionalDirection.BULLISH,
        "strength": 50.0,
        "confidence": 90.0,
        "bullish_score": 70.0,
        "bearish_score": 20.0,
        "agreement_count": 2,
        "conflict_count": 1,
        "supporting_domains": (
            "TREND",
            "STRUCTURE",
        ),
        "opposing_domains": (
            "LIQUIDITY",
        ),
    }

    arguments[
        field_name
    ] = -1

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be negative",
    ):
        InstitutionalBias(
            **arguments,  # type: ignore[arg-type]
        )


def test_rejects_strength_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "strength must equal the absolute difference"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.BULLISH,
            strength=40.0,
            confidence=90.0,
            bullish_score=70.0,
            bearish_score=20.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=(
                "TREND",
            ),
        )


def test_rejects_bullish_without_score_advantage() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bullish direction requires bullish_score"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.BULLISH,
            strength=0.0,
            confidence=50.0,
            bullish_score=40.0,
            bearish_score=40.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=(
                "TREND",
            ),
        )


def test_rejects_bearish_without_score_advantage() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Bearish direction requires bearish_score"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.BEARISH,
            strength=0.0,
            confidence=50.0,
            bullish_score=40.0,
            bearish_score=40.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=(
                "TREND",
            ),
        )


def test_rejects_neutral_unequal_scores() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Neutral direction requires equal bullish and "
            "bearish scores"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.NEUTRAL,
            strength=10.0,
            confidence=50.0,
            bullish_score=50.0,
            bearish_score=40.0,
            agreement_count=0,
            conflict_count=0,
        )


def test_rejects_unknown_with_scores() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Unknown direction requires zero bullish and "
            "bearish scores"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.UNKNOWN,
            strength=10.0,
            confidence=0.0,
            bullish_score=10.0,
            bearish_score=0.0,
            agreement_count=0,
            conflict_count=0,
        )


def test_rejects_domain_in_multiple_groups() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "A domain cannot appear in more than one bias "
            "classification"
        ),
    ):
        make_bias(
            opposing_domains=(
                "TREND",
            ),
        )


def test_rejects_agreement_count_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "agreement_count must match supporting_domains"
        ),
    ):
        make_bias(
            agreement_count=1,
        )


def test_rejects_conflict_count_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "conflict_count must match opposing_domains"
        ),
    ):
        make_bias(
            conflict_count=0,
        )


def test_rejects_neutral_with_supporting_domains() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Neutral or unknown bias cannot report supporting "
            "directional domains"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.NEUTRAL,
            strength=0.0,
            confidence=50.0,
            bullish_score=40.0,
            bearish_score=40.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=(
                "TREND",
            ),
        )


def test_rejects_non_tuple_domain_collection() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "supporting_domains must be a tuple"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.BULLISH,
            strength=50.0,
            confidence=90.0,
            bullish_score=70.0,
            bearish_score=20.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=[  # type: ignore[arg-type]
                "TREND",
            ],
        )


def test_rejects_non_string_domain() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "supporting_domains must contain strings"
        ),
    ):
        InstitutionalBias(
            direction=InstitutionalDirection.BULLISH,
            strength=50.0,
            confidence=90.0,
            bullish_score=70.0,
            bearish_score=20.0,
            agreement_count=1,
            conflict_count=0,
            supporting_domains=(
                123,  # type: ignore[arg-type]
            ),
        )


def test_empty_factory() -> None:
    result = InstitutionalBias.empty()

    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.strength == 0.0
    assert result.confidence == 0.0
    assert result.bullish_score == 0.0
    assert result.bearish_score == 0.0
    assert result.classified_domain_count == 0


def test_empty_factory_classifies_domains_unknown() -> None:
    result = InstitutionalBias.empty(
        domains=(
            "trend",
            "structure",
            "liquidity",
        )
    )

    assert result.unknown_domains == (
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
    )
    assert result.unresolved_domain_count == 3