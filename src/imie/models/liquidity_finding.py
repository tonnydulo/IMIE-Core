from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_point import LiquidityPoint
from imie.models.liquidity_types import (
    LiquidityImportance,
    LiquidityLocation,
    LiquidityState,
    LiquidityType,
)


@dataclass(frozen=True, slots=True)
class LiquidityFinding:
    """
    Represents the interpreted output of one liquidity detector.

    LiquidityPoint records the confirmed price location.
    LiquidityFinding adds classification, confidence,
    lifecycle state, source, and explainability.
    """

    point: LiquidityPoint
    liquidity_type: LiquidityType
    importance: LiquidityImportance
    location: LiquidityLocation
    confidence: float
    state: LiquidityState
    reason: str
    evidence: tuple[str, ...]
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.point, LiquidityPoint):
            raise TypeError(
                "LiquidityFinding point must be a LiquidityPoint."
            )

        if not isinstance(self.liquidity_type, LiquidityType):
            raise TypeError(
                "LiquidityFinding liquidity_type must be a LiquidityType."
            )

        if not isinstance(self.importance, LiquidityImportance):
            raise TypeError(
                "LiquidityFinding importance must be a LiquidityImportance."
            )

        if not isinstance(self.location, LiquidityLocation):
            raise TypeError(
                "LiquidityFinding location must be a LiquidityLocation."
            )

        if not isinstance(self.state, LiquidityState):
            raise TypeError(
                "LiquidityFinding state must be a LiquidityState."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "LiquidityFinding confidence must be between 0 and 100."
            )

        if not self.reason.strip():
            raise ValueError(
                "LiquidityFinding reason cannot be empty."
            )

        if not self.source.strip():
            raise ValueError(
                "LiquidityFinding source cannot be empty."
            )

        if any(not item.strip() for item in self.evidence):
            raise ValueError(
                "LiquidityFinding evidence cannot contain empty entries."
            )

    @property
    def is_active(self) -> bool:
        return self.state is LiquidityState.ACTIVE

    @property
    def is_major(self) -> bool:
        return self.importance is LiquidityImportance.MAJOR

    @property
    def is_internal(self) -> bool:
        return self.location is LiquidityLocation.INTERNAL

    @property
    def is_external(self) -> bool:
        return self.location is LiquidityLocation.EXTERNAL