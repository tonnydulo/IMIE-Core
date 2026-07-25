from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)
from imie.models.market_phase_type import (
    MarketPhaseType,
)


@dataclass(frozen=True, slots=True)
class ParticipationAnalysis:
    """
    Institutional interpretation of recent volume participation.
    """

    direction: InstitutionalDirection
    participation: str
    market_phase: MarketPhaseType

    average_volume: float
    recent_average_volume: float
    volume_ratio: float

    evaluated_bar_count: int
    recent_bar_count: int

    confidence: float
    opinion: str

    evidence: tuple[str, ...] = field(
        default_factory=tuple
    )
    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.direction,
            InstitutionalDirection,
        ):
            raise TypeError(
                "direction must be an "
                "InstitutionalDirection."
            )

        if not isinstance(
            self.market_phase,
            MarketPhaseType,
        ):
            raise TypeError(
                "market_phase must be a "
                "MarketPhaseType."
            )

        participation = (
            self.participation
            .strip()
            .upper()
        )

        if participation not in (
            "BULLISH",
            "BEARISH",
            "STRONG_NON_DIRECTIONAL",
            "NORMAL",
            "WEAK",
            "UNKNOWN",
        ):
            raise ValueError(
                "Unsupported participation state."
            )

        if self.evaluated_bar_count < 0:
            raise ValueError(
                "evaluated_bar_count cannot be negative."
            )

        if self.recent_bar_count < 0:
            raise ValueError(
                "recent_bar_count cannot be negative."
            )

        confidence = max(
            0.0,
            min(
                100.0,
                float(self.confidence),
            ),
        )

        opinion = self.opinion.strip()

        if not opinion:
            raise ValueError(
                "opinion cannot be empty."
            )

        object.__setattr__(
            self,
            "participation",
            participation,
        )

        object.__setattr__(
            self,
            "average_volume",
            float(self.average_volume),
        )

        object.__setattr__(
            self,
            "recent_average_volume",
            float(self.recent_average_volume),
        )

        object.__setattr__(
            self,
            "volume_ratio",
            float(self.volume_ratio),
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "opinion",
            opinion,
        )

        object.__setattr__(
            self,
            "evidence",
            tuple(
                str(item).strip()
                for item in self.evidence
                if str(item).strip()
            ),
        )

        object.__setattr__(
            self,
            "warnings",
            tuple(
                str(item).strip()
                for item in self.warnings
                if str(item).strip()
            ),
        )