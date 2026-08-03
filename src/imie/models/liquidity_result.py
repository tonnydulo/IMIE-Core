from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_pool import LiquidityPool
from imie.models.liquidity_types import LiquidityBias


@dataclass(frozen=True, slots=True)
class LiquidityResult:
    """
    Institutional reasoning produced by the LiquidityEngine.

    LiquidityResult summarizes the complete liquidity landscape
    after detector findings have been consolidated into
    institutional liquidity pools.

    This immutable result is consumed by LiquidityAnalyst and,
    later, by the DecisionDirector.
    """

    buy_side_pools: tuple[LiquidityPool, ...]
    sell_side_pools: tuple[LiquidityPool, ...]

    nearest_buy_side: LiquidityPool | None
    nearest_sell_side: LiquidityPool | None

    highest_confidence_pool: LiquidityPool | None
    highest_importance_pool: LiquidityPool | None

    active_pool_count: int
    major_pool_count: int

    average_confidence: float

    institutional_bias: LiquidityBias

    evidence: tuple[str, ...]
    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        self._validate_pool_collections()
        self._validate_optional_pools()

        if not isinstance(
            self.institutional_bias,
            LiquidityBias,
        ):
            raise TypeError(
                "LiquidityResult institutional_bias must be "
                "a LiquidityBias."
            )

        if self.active_pool_count < 0:
            raise ValueError(
                "LiquidityResult active_pool_count "
                "cannot be negative."
            )

        if self.major_pool_count < 0:
            raise ValueError(
                "LiquidityResult major_pool_count "
                "cannot be negative."
            )

        if self.major_pool_count > self.active_pool_count:
            raise ValueError(
                "LiquidityResult major_pool_count cannot exceed "
                "active_pool_count."
            )

        if not 0.0 <= self.average_confidence <= 100.0:
            raise ValueError(
                "LiquidityResult average_confidence must be "
                "between 0 and 100."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "LiquidityResult evidence entries must be "
                "non-empty strings."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.warnings
        ):
            raise ValueError(
                "LiquidityResult warning entries must be "
                "non-empty strings."
            )

        expected_active_count = self.total_pool_count

        if self.active_pool_count != expected_active_count:
            raise ValueError(
                "LiquidityResult active_pool_count must equal "
                "the number of buy-side and sell-side pools."
            )

        expected_major_count = sum(
            1
            for pool in self.all_pools
            if pool.is_major
        )

        if self.major_pool_count != expected_major_count:
            raise ValueError(
                "LiquidityResult major_pool_count must equal "
                "the number of major liquidity pools."
            )

    def _validate_pool_collections(self) -> None:
        for pool in self.buy_side_pools:
            if not isinstance(pool, LiquidityPool):
                raise TypeError(
                    "LiquidityResult buy_side_pools must contain "
                    "LiquidityPool objects."
                )

            if not pool.is_buy_side:
                raise ValueError(
                    "LiquidityResult buy_side_pools cannot contain "
                    "sell-side liquidity."
                )

        for pool in self.sell_side_pools:
            if not isinstance(pool, LiquidityPool):
                raise TypeError(
                    "LiquidityResult sell_side_pools must contain "
                    "LiquidityPool objects."
                )

            if not pool.is_sell_side:
                raise ValueError(
                    "LiquidityResult sell_side_pools cannot contain "
                    "buy-side liquidity."
                )

    def _validate_optional_pools(self) -> None:
        optional_pools = (
            self.nearest_buy_side,
            self.nearest_sell_side,
            self.highest_confidence_pool,
            self.highest_importance_pool,
        )

        for pool in optional_pools:
            if pool is not None and not isinstance(
                pool,
                LiquidityPool,
            ):
                raise TypeError(
                    "LiquidityResult optional pool fields must be "
                    "LiquidityPool objects or None."
                )

        if (
            self.nearest_buy_side is not None
            and not self.nearest_buy_side.is_buy_side
        ):
            raise ValueError(
                "LiquidityResult nearest_buy_side must contain "
                "buy-side liquidity."
            )

        if (
            self.nearest_sell_side is not None
            and not self.nearest_sell_side.is_sell_side
        ):
            raise ValueError(
                "LiquidityResult nearest_sell_side must contain "
                "sell-side liquidity."
            )

        if (
            self.nearest_buy_side is not None
            and self.nearest_buy_side not in self.buy_side_pools
        ):
            raise ValueError(
                "LiquidityResult nearest_buy_side must exist in "
                "buy_side_pools."
            )

        if (
            self.nearest_sell_side is not None
            and self.nearest_sell_side not in self.sell_side_pools
        ):
            raise ValueError(
                "LiquidityResult nearest_sell_side must exist in "
                "sell_side_pools."
            )

        if (
            self.highest_confidence_pool is not None
            and self.highest_confidence_pool not in self.all_pools
        ):
            raise ValueError(
                "LiquidityResult highest_confidence_pool must exist "
                "in the result pool collections."
            )

        if (
            self.highest_importance_pool is not None
            and self.highest_importance_pool not in self.all_pools
        ):
            raise ValueError(
                "LiquidityResult highest_importance_pool must exist "
                "in the result pool collections."
            )

    @property
    def all_pools(self) -> tuple[LiquidityPool, ...]:
        return (
            self.buy_side_pools
            + self.sell_side_pools
        )

    @property
    def total_pool_count(self) -> int:
        return len(self.all_pools)

    @property
    def has_buy_side(self) -> bool:
        return bool(self.buy_side_pools)

    @property
    def has_sell_side(self) -> bool:
        return bool(self.sell_side_pools)

    @property
    def has_major_liquidity(self) -> bool:
        return self.major_pool_count > 0

    @property
    def strongest_pool(self) -> LiquidityPool | None:
        return self.highest_confidence_pool

    @property
    def is_balanced(self) -> bool:
        return (
            self.institutional_bias
            is LiquidityBias.BALANCED
        )

    @property
    def is_unknown(self) -> bool:
        return (
            self.institutional_bias
            is LiquidityBias.UNKNOWN
        )