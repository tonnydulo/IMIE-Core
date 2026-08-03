from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.engines.order_blocks import (
    DisplacementScore,
    DisplacementScorer,
)
from imie.models import MarketBar


def make_bar(
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
    timestamp: int = 1,
) -> MarketBar:
    return MarketBar(
        symbol="SPY",
        timeframe="1m",
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def make_source_bar(
    *,
    open_price: float = 550.00,
    high: float = 550.10,
    low: float = 549.50,
    close: float = 549.80,
) -> MarketBar:
    return make_bar(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
        timestamp=1,
    )


def make_displacement_bar(
    *,
    open_price: float = 549.75,
    high: float = 550.70,
    low: float = 549.70,
    close: float = 550.60,
) -> MarketBar:
    return make_bar(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
        timestamp=2,
    )


def test_returns_displacement_score() -> None:
    scorer = DisplacementScorer()

    result = scorer.score(
        source=make_source_bar(),
        displacement=make_displacement_bar(),
    )

    assert isinstance(
        result,
        DisplacementScore,
    )


def test_zero_range_returns_zero_score() -> None:
    scorer = DisplacementScorer()

    displacement = make_displacement_bar(
        open_price=550.00,
        high=550.00,
        low=550.00,
        close=550.00,
    )

    result = scorer.score(
        source=make_source_bar(),
        displacement=displacement,
    )

    assert result.body_ratio_score == 0.0
    assert result.expansion_score == 0.0
    assert result.close_location_score == 0.0
    assert result.overall_score == 0.0


def test_zero_source_body_is_handled_safely() -> None:
    scorer = DisplacementScorer()

    source = make_source_bar(
        open_price=550.00,
        close=550.00,
    )

    result = scorer.score(
        source=source,
        displacement=make_displacement_bar(),
    )

    assert result.expansion_score == 0.0
    assert 0.0 <= result.overall_score <= 100.0


def test_body_ratio_score_is_calculated_correctly() -> None:
    scorer = DisplacementScorer()

    displacement = make_displacement_bar(
        open_price=550.00,
        high=551.00,
        low=549.00,
        close=551.00,
    )

    result = scorer.score(
        source=make_source_bar(),
        displacement=displacement,
    )

    assert result.body_ratio_score == pytest.approx(
        50.0,
    )


def test_expansion_score_is_calculated_correctly() -> None:
    scorer = DisplacementScorer(
        minimum_displacement_multiple=1.50,
    )

    source = make_source_bar(
        open_price=550.00,
        close=549.50,
    )

    displacement = make_displacement_bar(
        open_price=549.50,
        high=551.10,
        low=549.40,
        close=551.00,
    )

    result = scorer.score(
        source=source,
        displacement=displacement,
    )

    expected = min(
        100.0,
        (
            1.50
            / 0.50
            / 1.50
            * 70.0
        ),
    )

    assert result.expansion_score == pytest.approx(
        expected,
    )


def test_close_location_score_is_calculated_correctly() -> None:
    scorer = DisplacementScorer()

    displacement = make_displacement_bar(
        open_price=549.50,
        high=551.00,
        low=549.00,
        close=550.50,
    )

    result = scorer.score(
        source=make_source_bar(),
        displacement=displacement,
    )

    assert result.close_location_score == pytest.approx(
        75.0,
    )


def test_overall_score_uses_weighted_components() -> None:
    scorer = DisplacementScorer()

    source = make_source_bar(
        open_price=550.00,
        close=549.50,
    )

    displacement = make_displacement_bar(
        open_price=549.50,
        high=551.00,
        low=549.00,
        close=550.50,
    )

    result = scorer.score(
        source=source,
        displacement=displacement,
    )

    expected = (
        result.body_ratio_score * 0.45
        + result.expansion_score * 0.35
        + result.close_location_score * 0.20
    )

    assert result.overall_score == pytest.approx(
        round(expected, 2),
    )


@pytest.mark.parametrize(
    (
        "open_price",
        "high",
        "low",
        "close",
    ),
    [
        (
            549.00,
            551.00,
            549.00,
            551.00,
        ),
        (
            549.50,
            550.50,
            549.00,
            550.40,
        ),
        (
            550.00,
            550.10,
            549.90,
            550.05,
        ),
    ],
)
def test_overall_score_remains_between_zero_and_one_hundred(
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> None:
    scorer = DisplacementScorer()

    displacement = make_displacement_bar(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
    )

    result = scorer.score(
        source=make_source_bar(),
        displacement=displacement,
    )

    assert 0.0 <= result.overall_score <= 100.0


def test_larger_displacement_scores_higher() -> None:
    scorer = DisplacementScorer()

    source = make_source_bar(
        open_price=550.00,
        close=549.80,
    )

    weak = make_displacement_bar(
        open_price=549.80,
        high=550.20,
        low=549.70,
        close=550.10,
    )

    strong = make_displacement_bar(
        open_price=549.75,
        high=551.00,
        low=549.70,
        close=550.95,
    )

    weak_score = scorer.score(
        source=source,
        displacement=weak,
    )

    strong_score = scorer.score(
        source=source,
        displacement=strong,
    )

    assert (
        strong_score.overall_score
        > weak_score.overall_score
    )


def test_score_object_is_frozen() -> None:
    scorer = DisplacementScorer()

    result = scorer.score(
        source=make_source_bar(),
        displacement=make_displacement_bar(),
    )

    with pytest.raises(FrozenInstanceError):
        result.overall_score = 50.0  # type: ignore[misc]


def test_invalid_source_type_is_rejected() -> None:
    scorer = DisplacementScorer()

    with pytest.raises(
        TypeError,
    ):
        scorer.score(
            source=None,  # type: ignore[arg-type]
            displacement=make_displacement_bar(),
        )


def test_invalid_displacement_type_is_rejected() -> None:
    scorer = DisplacementScorer()

    with pytest.raises(
        TypeError,
    ):
        scorer.score(
            source=make_source_bar(),
            displacement=None,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "minimum_displacement_multiple",
    [
        0.0,
        -1.0,
    ],
)
def test_invalid_minimum_displacement_multiple_is_rejected(
    minimum_displacement_multiple: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="minimum_displacement_multiple must be positive",
    ):
        DisplacementScorer(
            minimum_displacement_multiple=(
                minimum_displacement_multiple
            ),
        )