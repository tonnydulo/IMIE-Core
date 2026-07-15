from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_pool import LiquidityPool
from imie.models.liquidity_types import SweepDirection


@dataclass(frozen=True, slots=True)
class SweepResult:
    """
    Represents the outcome of evaluating one liquidity pool
    for a confirmed liquidity sweep.

    A sweep occurs when price trades beyond resting liquidity
    and subsequently reclaims the pool boundary.

    SweepResult records the observation only. It does not mutate
    the LiquidityPool or make a trading decision.
    """

    pool: LiquidityPool

    swept: bool

    direction: SweepDirection

    penetration_price: float | None

    close_price: float

    reclaimed: bool

    confidence: float

    reason: str

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pool, LiquidityPool):
            raise TypeError(
                "SweepResult pool must be a LiquidityPool."
            )

        if not isinstance(self.direction, SweepDirection):
            raise TypeError(
                "SweepResult direction must be a SweepDirection."
            )

        if self.close_price <= 0.0:
            raise ValueError(
                "SweepResult close_price must be positive."
            )

        if (
            self.penetration_price is not None
            and self.penetration_price <= 0.0
        ):
            raise ValueError(
                "SweepResult penetration_price must be positive "
                "when provided."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "SweepResult confidence must be between 0 and 100."
            )

        if not self.reason.strip():
            raise ValueError(
                "SweepResult reason cannot be empty."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "SweepResult evidence entries must be "
                "non-empty strings."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.warnings
        ):
            raise ValueError(
                "SweepResult warning entries must be "
                "non-empty strings."
            )

        if self.swept:
            if self.direction is SweepDirection.NONE:
                raise ValueError(
                    "A confirmed sweep must have a direction."
                )

            if self.penetration_price is None:
                raise ValueError(
                    "A confirmed sweep must include a "
                    "penetration_price."
                )

            if not self.reclaimed:
                raise ValueError(
                    "A confirmed sweep must reclaim the "
                    "liquidity pool."
                )

        else:
            if self.direction is not SweepDirection.NONE:
                raise ValueError(
                    "A non-sweep result must use "
                    "SweepDirection.NONE."
                )

            if self.reclaimed:
                raise ValueError(
                    "A non-sweep result cannot be reclaimed."
                )

    @property
    def is_bullish(self) -> bool:
        return (
            self.swept
            and self.direction is SweepDirection.BULLISH
        )

    @property
    def is_bearish(self) -> bool:
        return (
            self.swept
            and self.direction is SweepDirection.BEARISH
        )

    @property
    def is_no_sweep(self) -> bool:
        return not self.swept

    @property
    def pool_price(self) -> float:
        return self.pool.price