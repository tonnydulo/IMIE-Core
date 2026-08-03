from __future__ import annotations

from dataclasses import dataclass

from imie.models import MarketBar


@dataclass(frozen=True, slots=True)
class OrderBlockCandidate:
    """
    Internal detector object.

    Represents a possible institutional order block before
    validation and promotion.

    This class belongs to the detector implementation and
    should never be exported from imie.models.
    """

    source_index: int
    displacement_index: int

    source_bar: MarketBar
    displacement_bar: MarketBar

    displacement_score: float

    @property
    def body_size(self) -> float:
        return abs(
            self.displacement_bar.close
            - self.displacement_bar.open
        )

    @property
    def range_size(self) -> float:
        return (
            self.displacement_bar.high
            - self.displacement_bar.low
        )

    @property
    def body_ratio(self) -> float:
        if self.range_size <= 0.0:
            return 0.0

        return (
            self.body_size
            / self.range_size
        )

    @property
    def close_location(self) -> float:
        if self.range_size <= 0.0:
            return 0.0

        return (
            (
                self.displacement_bar.close
                - self.displacement_bar.low
            )
            / self.range_size
        )

    @property
    def displacement(self) -> float:
        return (
            self.displacement_bar.close
            - self.source_bar.high
        )

    @property
    def expansion_multiple(self) -> float:
        source_body = abs(
            self.source_bar.close
            - self.source_bar.open
        )

        if source_body <= 0.0:
            return 0.0

        return (
            self.body_size
            / source_body
        )