from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_finding import LiquidityFinding
from imie.models.liquidity_types import (
    LiquidityImportance,
    LiquiditySide,
)


@dataclass(slots=True, frozen=True)
class LiquidityPool:
    """
    Represents an institutional liquidity pool.

    A liquidity pool is a cluster of one or more liquidity
    findings that together represent a single institutional
    objective.

    Pools are created by the LiquidityPoolBuilder and are
    consumed by higher-level reasoning engines.
    """

    price: float

    upper: float

    lower: float

    side: LiquiditySide

    importance: LiquidityImportance

    confidence: float

    strength: float

    findings: tuple[LiquidityFinding, ...]

    reason: str

    evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.price <= 0.0:
            raise ValueError(
                "LiquidityPool price must be positive."
            )

        if self.lower > self.upper:
            raise ValueError(
                "LiquidityPool lower cannot exceed upper."
            )

        if not isinstance(self.side, LiquiditySide):
            raise TypeError(
                "LiquidityPool side must be a LiquiditySide."
            )

        if not isinstance(
            self.importance,
            LiquidityImportance,
        ):
            raise TypeError(
                "LiquidityPool importance must be a LiquidityImportance."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "LiquidityPool confidence must be between 0 and 100."
            )

        if self.strength < 0.0:
            raise ValueError(
                "LiquidityPool strength cannot be negative."
            )

        if not self.findings:
            raise ValueError(
                "LiquidityPool must contain at least one finding."
            )

        if not self.reason.strip():
            raise ValueError(
                "LiquidityPool reason cannot be empty."
            )

        if any(not item.strip() for item in self.evidence):
            raise ValueError(
                "LiquidityPool evidence cannot contain empty entries."
            )

    @property
    def finding_count(self) -> int:
        """Number of findings contained in this pool."""
        return len(self.findings)

    @property
    def is_buy_side(self) -> bool:
        return self.side is LiquiditySide.BUY_SIDE

    @property
    def is_sell_side(self) -> bool:
        return self.side is LiquiditySide.SELL_SIDE

    @property
    def is_major(self) -> bool:
        return self.importance is LiquidityImportance.MAJOR