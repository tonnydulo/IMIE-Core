from __future__ import annotations

from dataclasses import dataclass

from imie.engines.order_blocks import (
    DisplacementScore,
    DisplacementScorer,
    OrderBlockDetector,
)

from tests.engines.order_blocks.test_order_block_detector import (
    make_displacement_bar,
    make_source_bar,
    make_structure,
)


@dataclass(frozen=True, slots=True)
class StubScorer(DisplacementScorer):

    def score(
        self,
        *,
        source,
        displacement,
    ) -> DisplacementScore:

        return DisplacementScore(
            body_ratio_score=10.0,
            expansion_score=20.0,
            close_location_score=30.0,
            overall_score=99.0,
        )


def test_detector_uses_external_displacement_scorer() -> None:
    detector = OrderBlockDetector(
        scorer=StubScorer(),
    )

    result = detector.detect(
        bars=(
            make_source_bar(),
            make_displacement_bar(),
        ),
        structure=make_structure(),
    )

    assert len(result) == 1
    assert result[0].strength == 99.0