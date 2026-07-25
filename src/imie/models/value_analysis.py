from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)
from imie.models.market_phase_type import (
    MarketPhaseType,
)


@dataclass(frozen=True, slots=True)
class ValueAnalysis:
    """
    Institutional interpretation of price relative to fair value.

    VWAP represents the first runtime fair-value reference.
    """

    direction: InstitutionalDirection
    value_state: str
    market_phase: MarketPhaseType

    price: float
    fair_value: float | None
    distance_to_value: float | None
    atr_distance_to_value: float | None

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

        value_state = (
            self.value_state
            .strip()
            .upper()
        )

        if value_state not in (
            "DISCOUNT",
            "FAIR_VALUE",
            "PREMIUM",
            "UNKNOWN",
        ):
            raise ValueError(
                "value_state must be DISCOUNT, "
                "FAIR_VALUE, PREMIUM, or UNKNOWN."
            )

        price = float(
            self.price
        )

        if price <= 0.0:
            raise ValueError(
                "price must be greater than zero."
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
            "value_state",
            value_state,
        )

        object.__setattr__(
            self,
            "price",
            price,
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