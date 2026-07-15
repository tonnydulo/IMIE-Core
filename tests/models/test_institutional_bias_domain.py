from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    InstitutionalBiasDomain,
    InstitutionalDirection,
)


def make_domain(
    *,
    domain: str = "TREND",
    direction: InstitutionalDirection = (
        InstitutionalDirection.BULLISH
    ),
    weight: float = 25.0,
    confidence: float = 80.0,
    weighted_score: float = 20.0,
    enabled: bool = True,
    evidence: tuple[str, ...] = (
        "Trend supports bullish continuation.",
    ),
    warnings: tuple[str, ...] = (),
) -> InstitutionalBiasDomain:
    return InstitutionalBiasDomain(
        domain=domain,
        direction=direction,
        weight=weight,
        confidence=confidence,
        weighted_score=weighted_score,
        enabled=enabled,
        evidence=evidence,
        warnings=warnings,
    )


def test_constructs_bias_domain() -> None:
    result = make_domain()

    assert isinstance(
        result,
        InstitutionalBiasDomain,
    )


def test_fields_are_stored() -> None:
    result = make_domain()

    assert result.domain == "TREND"
    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.weight == 25.0
    assert result.confidence == 80.0
    assert result.weighted_score == 20.0
    assert result.enabled is True


def test_domain_is_normalized() -> None:
    result = make_domain(
        domain=" trend ",
    )

    assert result.domain == "TREND"


def test_direction_alias_is_normalized() -> None:
    result = InstitutionalBiasDomain(
        domain="TREND",
        direction="long",  # type: ignore[arg-type]
        weight=25.0,
        confidence=80.0,
        weighted_score=20.0,
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )


def test_bullish_helper() -> None:
    result = make_domain()

    assert result.is_bullish is True
    assert result.is_bearish is False


def test_bearish_helper() -> None:
    result = make_domain(
        direction=InstitutionalDirection.BEARISH,
    )

    assert result.is_bearish is True
    assert result.is_bullish is False


def test_neutral_helper() -> None:
    result = make_domain(
        direction=InstitutionalDirection.NEUTRAL,
        weighted_score=0.0,
    )

    assert result.is_neutral is True
    assert result.is_directional is False
    assert result.contributes is False


def test_unknown_helper() -> None:
    result = make_domain(
        direction=InstitutionalDirection.UNKNOWN,
        weighted_score=0.0,
    )

    assert result.is_unknown is True
    assert result.is_directional is False
    assert result.contributes is False


def test_disabled_domain_helpers() -> None:
    result = make_domain(
        direction=InstitutionalDirection.BULLISH,
        confidence=0.0,
        weighted_score=0.0,
        enabled=False,
    )

    assert result.is_disabled is True
    assert result.is_bullish is False
    assert result.is_directional is False
    assert result.contributes is False


def test_bullish_contribution() -> None:
    result = make_domain()

    assert result.bullish_contribution == 20.0
    assert result.bearish_contribution == 0.0


def test_bearish_contribution() -> None:
    result = make_domain(
        direction=InstitutionalDirection.BEARISH,
    )

    assert result.bullish_contribution == 0.0
    assert result.bearish_contribution == 20.0


def test_neutral_has_zero_contributions() -> None:
    result = make_domain(
        direction=InstitutionalDirection.NEUTRAL,
        weighted_score=0.0,
    )

    assert result.bullish_contribution == 0.0
    assert result.bearish_contribution == 0.0


def test_zero_confidence_directional_domain_does_not_contribute() -> None:
    result = make_domain(
        confidence=0.0,
        weighted_score=0.0,
    )

    assert result.is_directional is True
    assert result.contributes is False


def test_has_evidence() -> None:
    result = make_domain()

    assert result.has_evidence is True


def test_has_no_evidence() -> None:
    result = make_domain(
        evidence=(),
    )

    assert result.has_evidence is False


def test_has_warnings() -> None:
    result = make_domain(
        warnings=(
            "Trend confidence is weak.",
        ),
    )

    assert result.has_warnings is True


def test_has_no_warnings() -> None:
    result = make_domain()

    assert result.has_warnings is False


def test_evidence_is_cleaned() -> None:
    result = make_domain(
        evidence=(
            "",
            "Trend supports bullish continuation.",
            "trend supports bullish continuation.",
            "  Structure agrees.  ",
        ),
    )

    assert result.evidence == (
        "Trend supports bullish continuation.",
        "Structure agrees.",
    )


def test_warnings_are_cleaned() -> None:
    result = make_domain(
        warnings=(
            "",
            "Trend confidence is weak.",
            "trend confidence is weak.",
        ),
    )

    assert result.warnings == (
        "Trend confidence is weak.",
    )


def test_numeric_values_are_rounded() -> None:
    result = InstitutionalBiasDomain(
        domain="TREND",
        direction=InstitutionalDirection.BULLISH,
        weight=25.004,
        confidence=79.996,
        weighted_score=20.0,
    )

    assert result.weight == 25.0
    assert result.confidence == 80.0
    assert result.weighted_score == 20.0


def test_create_calculates_bullish_weighted_score() -> None:
    result = InstitutionalBiasDomain.create(
        domain="TREND",
        direction=InstitutionalDirection.BULLISH,
        weight=25.0,
        confidence=80.0,
    )

    assert result.weighted_score == 20.0
    assert result.bullish_contribution == 20.0


def test_create_calculates_bearish_weighted_score() -> None:
    result = InstitutionalBiasDomain.create(
        domain="STRUCTURE",
        direction=InstitutionalDirection.BEARISH,
        weight=20.0,
        confidence=75.0,
    )

    assert result.weighted_score == 15.0
    assert result.bearish_contribution == 15.0


def test_create_neutral_has_zero_score() -> None:
    result = InstitutionalBiasDomain.create(
        domain="VALUE",
        direction=InstitutionalDirection.NEUTRAL,
        weight=5.0,
        confidence=90.0,
    )

    assert result.weighted_score == 0.0


def test_create_unknown_has_zero_score() -> None:
    result = InstitutionalBiasDomain.create(
        domain="AUCTION",
        direction=InstitutionalDirection.UNKNOWN,
        weight=10.0,
        confidence=90.0,
    )

    assert result.weighted_score == 0.0


def test_create_disabled_has_zero_score() -> None:
    result = InstitutionalBiasDomain.create(
        domain="LIQUIDITY",
        direction=InstitutionalDirection.BULLISH,
        weight=15.0,
        confidence=90.0,
        enabled=False,
    )

    assert result.weighted_score == 0.0
    assert result.is_disabled is True


def test_disabled_factory() -> None:
    result = InstitutionalBiasDomain.disabled(
        domain="AUCTION",
        weight=10.0,
    )

    assert result.domain == "AUCTION"
    assert result.enabled is False
    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.confidence == 0.0
    assert result.weighted_score == 0.0


def test_unknown_factory() -> None:
    result = InstitutionalBiasDomain.unknown(
        domain="VALUE",
        weight=5.0,
        confidence=25.0,
    )

    assert result.enabled is True
    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.confidence == 25.0
    assert result.weighted_score == 0.0


def test_model_is_frozen() -> None:
    result = make_domain()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.weight = 50.0  # type: ignore[misc]


def test_rejects_non_string_domain() -> None:
    with pytest.raises(
        TypeError,
        match="domain must be a string",
    ):
        make_domain(
            domain=123,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "domain",
    [
        "",
        " ",
    ],
)
def test_rejects_empty_domain(
    domain: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="domain cannot be empty",
    ):
        make_domain(
            domain=domain,
        )


def test_rejects_invalid_direction() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "direction must be an InstitutionalDirection"
        ),
    ):
        InstitutionalBiasDomain(
            domain="TREND",
            direction="SIDEWAYS",  # type: ignore[arg-type]
            weight=25.0,
            confidence=80.0,
            weighted_score=20.0,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "weight",
            -0.01,
        ),
        (
            "weight",
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
            "weighted_score",
            -0.01,
        ),
        (
            "weighted_score",
            100.01,
        ),
    ],
)
def test_rejects_values_outside_range(
    field_name: str,
    value: float,
) -> None:
    arguments: dict[str, object] = {
        "domain": "TREND",
        "direction": InstitutionalDirection.BULLISH,
        "weight": 25.0,
        "confidence": 80.0,
        "weighted_score": 20.0,
        "enabled": True,
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
        InstitutionalBiasDomain(
            **arguments,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "weight",
        "confidence",
        "weighted_score",
    ],
)
def test_rejects_boolean_numeric_values(
    field_name: str,
) -> None:
    arguments: dict[str, object] = {
        "domain": "TREND",
        "direction": InstitutionalDirection.BULLISH,
        "weight": 25.0,
        "confidence": 80.0,
        "weighted_score": 20.0,
        "enabled": True,
    }

    arguments[
        field_name
    ] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be numeric",
    ):
        InstitutionalBiasDomain(
            **arguments,  # type: ignore[arg-type]
        )


def test_rejects_non_boolean_enabled() -> None:
    with pytest.raises(
        TypeError,
        match="enabled must be a bool",
    ):
        InstitutionalBiasDomain(
            domain="TREND",
            direction=InstitutionalDirection.BULLISH,
            weight=25.0,
            confidence=80.0,
            weighted_score=20.0,
            enabled=1,  # type: ignore[arg-type]
        )


def test_rejects_incorrect_directional_weighted_score() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "weighted_score must equal weight multiplied by "
            "confidence divided by 100"
        ),
    ):
        make_domain(
            weighted_score=19.0,
        )


def test_rejects_neutral_nonzero_weighted_score() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "weighted_score must equal weight multiplied by "
            "confidence divided by 100"
        ),
    ):
        make_domain(
            direction=InstitutionalDirection.NEUTRAL,
            weighted_score=20.0,
        )


def test_rejects_unknown_nonzero_weighted_score() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "weighted_score must equal weight multiplied by "
            "confidence divided by 100"
        ),
    ):
        make_domain(
            direction=InstitutionalDirection.UNKNOWN,
            weighted_score=20.0,
        )


def test_rejects_disabled_nonzero_weighted_score() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "weighted_score must equal weight multiplied by "
            "confidence divided by 100"
        ),
    ):
        make_domain(
            enabled=False,
            weighted_score=20.0,
        )


def test_rejects_non_tuple_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be a tuple",
    ):
        make_domain(
            evidence=[  # type: ignore[arg-type]
                "Evidence",
            ],
        )


def test_rejects_non_tuple_warnings() -> None:
    with pytest.raises(
        TypeError,
        match="warnings must be a tuple",
    ):
        make_domain(
            warnings=[  # type: ignore[arg-type]
                "Warning",
            ],
        )


def test_rejects_non_string_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must contain strings",
    ):
        make_domain(
            evidence=(
                123,  # type: ignore[arg-type]
            ),
        )


def test_rejects_non_string_warning() -> None:
    with pytest.raises(
        TypeError,
        match="warnings must contain strings",
    ):
        make_domain(
            warnings=(
                123,  # type: ignore[arg-type]
            ),
        )