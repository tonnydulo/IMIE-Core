from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)
from imie.models.market_phase_type import (
    MarketPhaseType,
)


@dataclass(frozen=True, slots=True)
class PressureAnalysis:
    """
    Institutional interpretation of recent candle pressure.
    """

    direction: InstitutionalDirection
    pressure: str
    market_phase: MarketPhaseType

    bullish_score: float
    bearish_score: float

    evaluated_bar_count: int
    directional_bar_count: int

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

        pressure = self.pressure.strip().upper()

        if pressure not in (
            "BUYING",
            "SELLING",
            "BALANCED",
            "BUYING_EXHAUSTED",
            "SELLING_EXHAUSTED",
            "UNKNOWN",
        ):
            raise ValueError(
                "Unsupported pressure state."
            )

        if self.evaluated_bar_count < 0:
            raise ValueError(
                "evaluated_bar_count cannot be negative."
            )

        if self.directional_bar_count < 0:
            raise ValueError(
                "directional_bar_count cannot be negative."
            )

        bullish_score = max(
            0.0,
            min(
                100.0,
                float(self.bullish_score),
            ),
        )

        bearish_score = max(
            0.0,
            min(
                100.0,
                float(self.bearish_score),
            ),
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
            "pressure",
            pressure,
        )

        object.__setattr__(
            self,
            "bullish_score",
            bullish_score,
        )

        object.__setattr__(
            self,
            "bearish_score",
            bearish_score,
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