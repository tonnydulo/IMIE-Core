from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_pool import LiquidityPool
from imie.models.liquidity_result import LiquidityResult
from imie.models.liquidity_types import (
    LiquidityBias,
    LiquidityImportance,
    LiquiditySide,
)


_IMPORTANCE_RANK: dict[LiquidityImportance, int] = {
    LiquidityImportance.MINOR: 1,
    LiquidityImportance.INTERMEDIATE: 2,
    LiquidityImportance.MAJOR: 3,
}


@dataclass(frozen=True, slots=True)
class LiquidityEngine:
    """
    Evaluates an existing institutional liquidity landscape.

    The LiquidityEngine does not detect swings, identify equal
    highs or lows, or build liquidity pools. It receives completed
    LiquidityPool objects and summarizes them into an immutable
    LiquidityResult.

    Responsibilities:
    - separate buy-side and sell-side pools;
    - identify the nearest pool on each side;
    - identify the highest-confidence pool;
    - identify the highest-importance pool;
    - calculate pool counts and average confidence;
    - determine institutional liquidity bias;
    - produce explainable evidence and warnings.
    """

    weak_confidence_threshold: float = 70.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.weak_confidence_threshold <= 100.0:
            raise ValueError(
                "LiquidityEngine weak_confidence_threshold "
                "must be between 0 and 100."
            )

    def evaluate(
        self,
        pools: tuple[LiquidityPool, ...],
    ) -> LiquidityResult:
        """
        Evaluate completed liquidity pools.

        Until current market price is introduced into the liquidity
        context, nearest buy-side means the lowest-priced buy-side
        pool and nearest sell-side means the highest-priced
        sell-side pool.
        """
        self._validate_pools(pools)

        buy_side_pools, sell_side_pools = self._split_by_side(
            pools
        )

        nearest_buy_side = self._nearest_buy_side(
            buy_side_pools
        )

        nearest_sell_side = self._nearest_sell_side(
            sell_side_pools
        )

        highest_confidence_pool = (
            self._highest_confidence_pool(pools)
        )

        highest_importance_pool = (
            self._highest_importance_pool(pools)
        )

        active_pool_count = len(pools)

        major_pool_count = sum(
            1
            for pool in pools
            if pool.is_major
        )

        average_confidence = (
            self._calculate_average_confidence(pools)
        )

        institutional_bias = (
            self._determine_institutional_bias(
                buy_side_pools=buy_side_pools,
                sell_side_pools=sell_side_pools,
            )
        )

        evidence = self._build_evidence(
            pools=pools,
            buy_side_pools=buy_side_pools,
            sell_side_pools=sell_side_pools,
            average_confidence=average_confidence,
            institutional_bias=institutional_bias,
            highest_confidence_pool=highest_confidence_pool,
            highest_importance_pool=highest_importance_pool,
        )

        warnings = self._build_warnings(
            buy_side_pools=buy_side_pools,
            sell_side_pools=sell_side_pools,
            average_confidence=average_confidence,
        )

        return LiquidityResult(
            buy_side_pools=buy_side_pools,
            sell_side_pools=sell_side_pools,
            nearest_buy_side=nearest_buy_side,
            nearest_sell_side=nearest_sell_side,
            highest_confidence_pool=highest_confidence_pool,
            highest_importance_pool=highest_importance_pool,
            active_pool_count=active_pool_count,
            major_pool_count=major_pool_count,
            average_confidence=average_confidence,
            institutional_bias=institutional_bias,
            evidence=evidence,
            warnings=warnings,
        )

    @staticmethod
    def _validate_pools(
        pools: tuple[LiquidityPool, ...],
    ) -> None:
        for pool in pools:
            if not isinstance(pool, LiquidityPool):
                raise TypeError(
                    "LiquidityEngine requires LiquidityPool objects."
                )

    @staticmethod
    def _split_by_side(
        pools: tuple[LiquidityPool, ...],
    ) -> tuple[
        tuple[LiquidityPool, ...],
        tuple[LiquidityPool, ...],
    ]:
        buy_side_pools = tuple(
            sorted(
                (
                    pool
                    for pool in pools
                    if pool.side is LiquiditySide.BUY_SIDE
                ),
                key=lambda pool: pool.price,
            )
        )

        sell_side_pools = tuple(
            sorted(
                (
                    pool
                    for pool in pools
                    if pool.side is LiquiditySide.SELL_SIDE
                ),
                key=lambda pool: pool.price,
            )
        )

        return buy_side_pools, sell_side_pools

    @staticmethod
    def _nearest_buy_side(
        pools: tuple[LiquidityPool, ...],
    ) -> LiquidityPool | None:
        if not pools:
            return None

        return pools[0]

    @staticmethod
    def _nearest_sell_side(
        pools: tuple[LiquidityPool, ...],
    ) -> LiquidityPool | None:
        if not pools:
            return None

        return pools[-1]

    @staticmethod
    def _highest_confidence_pool(
        pools: tuple[LiquidityPool, ...],
    ) -> LiquidityPool | None:
        if not pools:
            return None

        return max(
            pools,
            key=lambda pool: (
                pool.confidence,
                pool.strength,
            ),
        )

    @staticmethod
    def _highest_importance_pool(
        pools: tuple[LiquidityPool, ...],
    ) -> LiquidityPool | None:
        if not pools:
            return None

        return max(
            pools,
            key=lambda pool: (
                _IMPORTANCE_RANK[pool.importance],
                pool.confidence,
                pool.strength,
            ),
        )

    @staticmethod
    def _calculate_average_confidence(
        pools: tuple[LiquidityPool, ...],
    ) -> float:
        if not pools:
            return 0.0

        return round(
            sum(
                pool.confidence
                for pool in pools
            )
            / len(pools),
            2,
        )

    @staticmethod
    def _determine_institutional_bias(
        *,
        buy_side_pools: tuple[LiquidityPool, ...],
        sell_side_pools: tuple[LiquidityPool, ...],
    ) -> LiquidityBias:
        if not buy_side_pools and not sell_side_pools:
            return LiquidityBias.UNKNOWN

        if len(buy_side_pools) > len(sell_side_pools):
            return LiquidityBias.BUY_SIDE_DOMINANT

        if len(sell_side_pools) > len(buy_side_pools):
            return LiquidityBias.SELL_SIDE_DOMINANT

        return LiquidityBias.BALANCED

    @staticmethod
    def _build_evidence(
        *,
        pools: tuple[LiquidityPool, ...],
        buy_side_pools: tuple[LiquidityPool, ...],
        sell_side_pools: tuple[LiquidityPool, ...],
        average_confidence: float,
        institutional_bias: LiquidityBias,
        highest_confidence_pool: LiquidityPool | None,
        highest_importance_pool: LiquidityPool | None,
    ) -> tuple[str, ...]:
        evidence: list[str] = [
            (
                f"Detected {len(pools)} active liquidity "
                f"pool{'' if len(pools) == 1 else 's'}."
            ),
            (
                f"Buy-side pools: "
                f"{len(buy_side_pools)}."
            ),
            (
                f"Sell-side pools: "
                f"{len(sell_side_pools)}."
            ),
            (
                "Average pool confidence: "
                f"{average_confidence:.2f}."
            ),
            (
                "Institutional liquidity bias: "
                f"{institutional_bias.value}."
            ),
        ]

        if highest_confidence_pool is not None:
            evidence.append(
                "Highest-confidence liquidity pool is "
                f"{highest_confidence_pool.side.value} at "
                f"{highest_confidence_pool.price:.4f} with "
                f"{highest_confidence_pool.confidence:.2f} "
                "confidence."
            )

        if highest_importance_pool is not None:
            evidence.append(
                "Highest-importance liquidity pool is "
                f"{highest_importance_pool.importance.value} "
                f"{highest_importance_pool.side.value} liquidity "
                f"at {highest_importance_pool.price:.4f}."
            )

        return tuple(evidence)

    def _build_warnings(
        self,
        *,
        buy_side_pools: tuple[LiquidityPool, ...],
        sell_side_pools: tuple[LiquidityPool, ...],
        average_confidence: float,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if not buy_side_pools and not sell_side_pools:
            warnings.append(
                "No active liquidity pools."
            )

        if not buy_side_pools:
            warnings.append(
                "No buy-side liquidity detected."
            )

        if not sell_side_pools:
            warnings.append(
                "No sell-side liquidity detected."
            )

        if (
            average_confidence
            < self.weak_confidence_threshold
        ):
            warnings.append(
                "Average liquidity confidence is weak."
            )

        return tuple(warnings)