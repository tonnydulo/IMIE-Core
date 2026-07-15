from __future__ import annotations

from dataclasses import dataclass

from imie.engines.order_blocks.displacement_score import (
    DisplacementScore,
)
from imie.models import MarketBar


@dataclass(frozen=True, slots=True)
class DisplacementScorer:
    """
    Scores institutional displacement candles.

    The scorer measures:

    - body dominance;
    - expansion relative to the source candle;
    - close location within the displacement range;
    - combined displacement quality.

    It does not detect order blocks or make trading decisions.
    """

    minimum_displacement_multiple: float = 1.50

    def __post_init__(self) -> None:
        if self.minimum_displacement_multiple <= 0.0:
            raise ValueError(
                "minimum_displacement_multiple must be positive."
            )

    def score(
        self,
        *,
        source: MarketBar,
        displacement: MarketBar,
    ) -> DisplacementScore:
        if not isinstance(
            source,
            MarketBar,
        ):
            raise TypeError(
                "source must be a MarketBar."
            )

        if not isinstance(
            displacement,
            MarketBar,
        ):
            raise TypeError(
                "displacement must be a MarketBar."
            )

        body = abs(
            displacement.close
            - displacement.open
        )

        candle_range = (
            displacement.high
            - displacement.low
        )

        source_body = abs(
            source.close
            - source.open
        )

        if candle_range <= 0.0:
            return DisplacementScore(
                body_ratio_score=0.0,
                expansion_score=0.0,
                close_location_score=0.0,
                overall_score=0.0,
            )

        body_ratio_score = (
            body
            / candle_range
            * 100.0
        )

        if source_body <= 0.0:
            expansion_score = 0.0
        else:
            expansion_score = min(
                100.0,
                (
                    body
                    / source_body
                    / self.minimum_displacement_multiple
                    * 70.0
                ),
            )

        close_location_score = (
            (
                displacement.close
                - displacement.low
            )
            / candle_range
            * 100.0
        )

        overall = (
            body_ratio_score * 0.45
            + expansion_score * 0.35
            + close_location_score * 0.20
        )

        return DisplacementScore(
            body_ratio_score=round(
                body_ratio_score,
                2,
            ),
            expansion_score=round(
                expansion_score,
                2,
            ),
            close_location_score=round(
                close_location_score,
                2,
            ),
            overall_score=round(
                max(
                    0.0,
                    min(
                        100.0,
                        overall,
                    ),
                ),
                2,
            ),
        )