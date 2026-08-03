from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    LiquidityBias,
    LiquidityPool,
)


@dataclass(frozen=True, slots=True)
class LiquidityAnalysis:
    """
    Institutional interpretation of the liquidity landscape.

    Unlike LiquidityResult, which summarizes detected liquidity,
    LiquidityAnalysis expresses what that liquidity implies from
    an institutional perspective.
    """

    institutional_bias: LiquidityBias

    nearest_active_buy_pool: LiquidityPool | None

    nearest_active_sell_pool: LiquidityPool | None

    strongest_pool: LiquidityPool | None

    active_pool_count: int

    swept_pool_count: int

    consumed_pool_count: int

    confidence: float

    opinion: str

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    def __post_init__(self) -> None:

        if not isinstance(
            self.institutional_bias,
            LiquidityBias,
        ):
            raise TypeError(
                "institutional_bias must be "
                "a LiquidityBias."
            )

        for name, value in (
            ("active_pool_count", self.active_pool_count),
            ("swept_pool_count", self.swept_pool_count),
            ("consumed_pool_count", self.consumed_pool_count),
        ):
            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative."
                )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "confidence must be between 0 and 100."
            )

        if not self.opinion.strip():
            raise ValueError(
                "opinion cannot be empty."
            )

        if any(
            not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "Evidence entries cannot be empty."
            )

        if any(
            not item.strip()
            for item in self.warnings
        ):
            raise ValueError(
                "Warning entries cannot be empty."
            )

        for pool in (
            self.nearest_active_buy_pool,
            self.nearest_active_sell_pool,
            self.strongest_pool,
        ):
            if pool is not None and not isinstance(
                pool,
                LiquidityPool,
            ):
                raise TypeError(
                    "Optional pool fields must contain "
                    "LiquidityPool objects."
                )

    @property
    def has_active_buy_liquidity(self) -> bool:
        return self.nearest_active_buy_pool is not None

    @property
    def has_active_sell_liquidity(self) -> bool:
        return self.nearest_active_sell_pool is not None

    @property
    def has_major_liquidity(self) -> bool:
        return self.strongest_pool is not None

    @property
    def total_known_pools(self) -> int:
        return (
            self.active_pool_count
            + self.swept_pool_count
            + self.consumed_pool_count
        )