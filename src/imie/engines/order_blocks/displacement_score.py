from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DisplacementScore:
    """
    Immutable normalized displacement-quality result.

    All component scores and the overall score must remain
    between 0 and 100.
    """

    body_ratio_score: float
    expansion_score: float
    close_location_score: float
    overall_score: float

    def __post_init__(self) -> None:
        for name, value in (
            (
                "body_ratio_score",
                self.body_ratio_score,
            ),
            (
                "expansion_score",
                self.expansion_score,
            ),
            (
                "close_location_score",
                self.close_location_score,
            ),
            (
                "overall_score",
                self.overall_score,
            ),
        ):
            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100."
                )