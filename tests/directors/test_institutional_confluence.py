from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    InstitutionalConfluence,
)


def make_confluence(
    *,
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

    adjustments = {
        0: 0.0,
        1: 2.0,
        2: 5.0,
        3: 8.0,
    }

    return InstitutionalConfluence(
        score=score,
        structure_support=structure_support,
        liquidity_support=liquidity_support,
        order_block_support=order_block_support,
        agreement_count=agreement_count,
        confidence_adjustment=(
            adjustments[
                agreement_count
            ]
        ),
        evidence=evidence,
        warnings=warnings,
    )


def test_constructs_empty_confluence() -> None:
    result = make_confluence()

    assert isinstance(
        result,
        InstitutionalConfluence,
    )

    assert result.score == 0.0
    assert result.agreement_count == 0
    assert result.confidence_adjustment == 0.0


def test_structure_only_score() -> None:
    result = make_confluence(
        structure_support=True,
    )

    assert result.score == 40.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_liquidity_only_score() -> None:
    result = make_confluence(
        liquidity_support=True,
    )

    assert result.score == 30.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_order_block_only_score() -> None:
    result = make_confluence(
        order_block_support=True,
    )

    assert result.score == 30.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_structure_and_liquidity_score() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
    )

    assert result.score == 70.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_structure_and_order_block_score() -> None:
    result = make_confluence(
        structure_support=True,
        order_block_support=True,
    )

    assert result.score == 70.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_liquidity_and_order_block_score() -> None:
    result = make_confluence(
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.score == 60.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_full_agreement_score() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.score == 100.0
    assert result.agreement_count == 3
    assert result.confidence_adjustment == 8.0


def test_support_flags_are_stored() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=False,
        order_block_support=True,
    )

    assert result.structure_support is True
    assert result.liquidity_support is False
    assert result.order_block_support is True


def test_has_support() -> None:
    result = make_confluence(
        structure_support=True,
    )

    assert result.has_support is True


def test_has_no_support() -> None:
    result = make_confluence()

    assert result.has_support is False


def test_has_full_agreement() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.has_full_agreement is True


def test_does_not_have_full_agreement() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
    )

    assert result.has_full_agreement is False


@pytest.mark.parametrize(
    (
        "structure_support",
        "liquidity_support",
        "order_block_support",
    ),
    [
        (
            True,
            False,
            False,
        ),
        (
            False,
            True,
            False,
        ),
        (
            False,
            False,
            True,
        ),
        (
            True,
            True,
            False,
        ),
        (
            True,
            False,
            True,
        ),
        (
            False,
            True,
            True,
        ),
    ],
)
def test_has_partial_agreement(
    structure_support: bool,
    liquidity_support: bool,
    order_block_support: bool,
) -> None:
    result = make_confluence(
        structure_support=structure_support,
        liquidity_support=liquidity_support,
        order_block_support=order_block_support,
    )

    assert result.has_partial_agreement is True


def test_full_agreement_is_not_partial() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.has_partial_agreement is False


def test_no_agreement_is_not_partial() -> None:
    result = make_confluence()

    assert result.has_partial_agreement is False


def test_has_no_agreement() -> None:
    result = make_confluence()

    assert result.has_no_agreement is True


def test_supporting_domains_empty() -> None:
    result = make_confluence()

    assert result.supporting_domains == ()


def test_supporting_domains_structure() -> None:
    result = make_confluence(
        structure_support=True,
    )

    assert result.supporting_domains == (
        "STRUCTURE",
    )


def test_supporting_domains_liquidity() -> None:
    result = make_confluence(
        liquidity_support=True,
    )

    assert result.supporting_domains == (
        "LIQUIDITY",
    )


def test_supporting_domains_order_block() -> None:
    result = make_confluence(
        order_block_support=True,
    )

    assert result.supporting_domains == (
        "ORDER_BLOCK",
    )


def test_supporting_domains_all() -> None:
    result = make_confluence(
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
    )

    assert result.supporting_domains == (
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
    )


def test_evidence_is_stored() -> None:
    result = make_confluence(
        evidence=(
            "Structure supports the setup.",
        ),
    )

    assert result.evidence == (
        "Structure supports the setup.",
    )


def test_warnings_are_stored() -> None:
    result = make_confluence(
        warnings=(
            "Institutional agreement is weak.",
        ),
    )

    assert result.warnings == (
        "Institutional agreement is weak.",
    )


def test_evidence_is_cleaned() -> None:
    result = make_confluence(
        evidence=(
            "",
            "Structure supports the setup.",
            "structure supports the setup.",
            "  Liquidity supports the setup.  ",
            " ",
        ),
    )

    assert result.evidence == (
        "Structure supports the setup.",
        "Liquidity supports the setup.",
    )


def test_warnings_are_cleaned() -> None:
    result = make_confluence(
        warnings=(
            "",
            "Institutional signals disagree.",
            "institutional signals disagree.",
            " ",
        ),
    )

    assert result.warnings == (
        "Institutional signals disagree.",
    )


def test_model_is_frozen() -> None:
    result = make_confluence()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.score = 50.0  # type: ignore[misc]


@pytest.mark.parametrize(
    "score",
    [
        -0.01,
        100.01,
    ],
)
def test_rejects_score_outside_range(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score must be between 0 and 100",
    ):
        InstitutionalConfluence(
            score=score,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
        )


@pytest.mark.parametrize(
    "agreement_count",
    [
        -1,
        4,
    ],
)
def test_rejects_agreement_count_outside_range(
    agreement_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "agreement_count must be between 0 and 3"
        ),
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=agreement_count,
            confidence_adjustment=0.0,
        )


@pytest.mark.parametrize(
    "confidence_adjustment",
    [
        -0.01,
        8.01,
    ],
)
def test_rejects_adjustment_outside_range(
    confidence_adjustment: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "confidence_adjustment must be between 0 and 8"
        ),
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=confidence_adjustment,
        )


def test_rejects_agreement_count_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "agreement_count must match the number of "
            "supporting institutional domains"
        ),
    ):
        InstitutionalConfluence(
            score=40.0,
            structure_support=True,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
        )


@pytest.mark.parametrize(
    (
        "agreement_count",
        "confidence_adjustment",
    ),
    [
        (
            0,
            2.0,
        ),
        (
            1,
            0.0,
        ),
        (
            2,
            8.0,
        ),
        (
            3,
            5.0,
        ),
    ],
)
def test_rejects_adjustment_mismatch(
    agreement_count: int,
    confidence_adjustment: float,
) -> None:
    flags = {
        0: (
            False,
            False,
            False,
        ),
        1: (
            True,
            False,
            False,
        ),
        2: (
            True,
            True,
            False,
        ),
        3: (
            True,
            True,
            True,
        ),
    }

    structure, liquidity, order_block = (
        flags[
            agreement_count
        ]
    )

    score = (
        (40.0 if structure else 0.0)
        + (30.0 if liquidity else 0.0)
        + (30.0 if order_block else 0.0)
    )

    with pytest.raises(
        ValueError,
        match=(
            "confidence_adjustment does not match "
            "agreement_count"
        ),
    ):
        InstitutionalConfluence(
            score=score,
            structure_support=structure,
            liquidity_support=liquidity,
            order_block_support=order_block,
            agreement_count=agreement_count,
            confidence_adjustment=confidence_adjustment,
        )


@pytest.mark.parametrize(
    (
        "score",
        "structure_support",
        "liquidity_support",
        "order_block_support",
        "agreement_count",
        "confidence_adjustment",
    ),
    [
        (
            30.0,
            True,
            False,
            False,
            1,
            2.0,
        ),
        (
            40.0,
            False,
            True,
            False,
            1,
            2.0,
        ),
        (
            70.0,
            False,
            True,
            True,
            2,
            5.0,
        ),
        (
            90.0,
            True,
            True,
            True,
            3,
            8.0,
        ),
    ],
)
def test_rejects_score_weight_mismatch(
    score: float,
    structure_support: bool,
    liquidity_support: bool,
    order_block_support: bool,
    agreement_count: int,
    confidence_adjustment: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "score must match the configured "
            "institutional support weights"
        ),
    ):
        InstitutionalConfluence(
            score=score,
            structure_support=structure_support,
            liquidity_support=liquidity_support,
            order_block_support=order_block_support,
            agreement_count=agreement_count,
            confidence_adjustment=confidence_adjustment,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "structure_support",
            1,
        ),
        (
            "liquidity_support",
            "yes",
        ),
        (
            "order_block_support",
            None,
        ),
    ],
)
def test_rejects_non_boolean_support_flags(
    field_name: str,
    value: object,
) -> None:
    values: dict[str, object] = {
        "structure_support": False,
        "liquidity_support": False,
        "order_block_support": False,
    }

    values[
        field_name
    ] = value

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=values[
                "structure_support"
            ],  # type: ignore[arg-type]
            liquidity_support=values[
                "liquidity_support"
            ],  # type: ignore[arg-type]
            order_block_support=values[
                "order_block_support"
            ],  # type: ignore[arg-type]
            agreement_count=0,
            confidence_adjustment=0.0,
        )


def test_rejects_non_tuple_evidence() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "evidence and warnings must be tuples"
        ),
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
            evidence=[  # type: ignore[arg-type]
                "Evidence",
            ],
        )


def test_rejects_non_tuple_warnings() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "evidence and warnings must be tuples"
        ),
    ):
        InstitutionalConfluence(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
            warnings=[  # type: ignore[arg-type]
                "Warning",
            ],
        )


def test_empty_factory() -> None:
    result = InstitutionalConfluence.empty()

    assert result.score == 0.0
    assert result.agreement_count == 0
    assert result.confidence_adjustment == 0.0
    assert result.has_no_agreement is True


def test_empty_factory_preserves_evidence_and_warnings() -> None:
    result = InstitutionalConfluence.empty(
        evidence=(
            "No institutional support detected.",
        ),
        warnings=(
            "Institutional agreement is unavailable.",
        ),
    )

    assert result.evidence == (
        "No institutional support detected.",
    )

    assert result.warnings == (
        "Institutional agreement is unavailable.",
    )