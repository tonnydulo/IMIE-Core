from __future__ import annotations

from dataclasses import dataclass

from imie.models import AnalystResult


@dataclass(frozen=True, slots=True)
class DecisionContext:
    """
    Consolidated institutional intelligence used by the
    DecisionDirector.

    DecisionContext represents the complete institutional
    picture immediately before a trading decision.
    """

    analyst_results: tuple[
        AnalystResult,
        ...
    ]

    average_confidence: float

    agreement_score: float

    conflict_score: float

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    @property
    def analyst_count(self) -> int:
        return len(self.analyst_results)

    @property
    def unanimous(self) -> bool:
        return self.conflict_score == 0.0