from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    LiquidityPool,
    LiquiditySide,
    MarketBar,
    SweepDirection,
    SweepResult,
)


@dataclass(frozen=True, slots=True)
class SweepDetector:
    """
    Evaluates completed market bars against existing
    institutional liquidity pools.

    This detector identifies confirmed liquidity sweeps
    but does not modify pool state or lifecycle.
    """

    confirmed_confidence: float = 95.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confirmed_confidence <= 100.0:
            raise ValueError(
                "confirmed_confidence must be between 0 and 100."
            )

    def detect(
        self,
        bar: MarketBar,
        pools: tuple[LiquidityPool, ...],
    ) -> tuple[SweepResult, ...]:

        self._validate_inputs(bar, pools)

        return tuple(
            self._evaluate_pool(bar, pool)
            for pool in pools
        )

    @staticmethod
    def _validate_inputs(
        bar: MarketBar,
        pools: tuple[LiquidityPool, ...],
    ) -> None:

        if not isinstance(bar, MarketBar):
            raise TypeError(
                "bar must be a MarketBar."
            )

        for pool in pools:
            if not isinstance(pool, LiquidityPool):
                raise TypeError(
                    "pools must contain LiquidityPool objects."
                )

    def _evaluate_pool(
        self,
        bar: MarketBar,
        pool: LiquidityPool,
    ) -> SweepResult:

        if pool.side is LiquiditySide.BUY_SIDE:
            return self._detect_buy_side(
                bar,
                pool,
            )

        return self._detect_sell_side(
            bar,
            pool,
        )

    def _detect_buy_side(
        self,
        bar: MarketBar,
        pool: LiquidityPool,
    ) -> SweepResult:

        penetrated = bar.high > pool.upper
        reclaimed = bar.close < pool.upper

        if penetrated and reclaimed:
            return SweepResult(
                pool=pool,
                swept=True,
                direction=SweepDirection.BEARISH,
                penetration_price=bar.high,
                close_price=bar.close,
                reclaimed=True,
                confidence=self.confirmed_confidence,
                reason=(
                    "Buy-side liquidity swept and reclaimed."
                ),
                evidence=(
                    "High exceeded buy-side liquidity.",
                    "Close reclaimed the liquidity pool.",
                    "Confirmed bearish liquidity sweep.",
                ),
                warnings=(),
            )

        return self._no_sweep(
            pool,
            bar.close,
        )

    def _detect_sell_side(
        self,
        bar: MarketBar,
        pool: LiquidityPool,
    ) -> SweepResult:

        penetrated = bar.low < pool.lower
        reclaimed = bar.close > pool.lower

        if penetrated and reclaimed:
            return SweepResult(
                pool=pool,
                swept=True,
                direction=SweepDirection.BULLISH,
                penetration_price=bar.low,
                close_price=bar.close,
                reclaimed=True,
                confidence=self.confirmed_confidence,
                reason=(
                    "Sell-side liquidity swept and reclaimed."
                ),
                evidence=(
                    "Low exceeded sell-side liquidity.",
                    "Close reclaimed the liquidity pool.",
                    "Confirmed bullish liquidity sweep.",
                ),
                warnings=(),
            )

        return self._no_sweep(
            pool,
            bar.close,
        )

    @staticmethod
    def _no_sweep(
        pool: LiquidityPool,
        close_price: float,
    ) -> SweepResult:

        return SweepResult(
            pool=pool,
            swept=False,
            direction=SweepDirection.NONE,
            penetration_price=None,
            close_price=close_price,
            reclaimed=False,
            confidence=0.0,
            reason="No confirmed liquidity sweep.",
            evidence=(
                "Price did not complete a confirmed liquidity sweep.",
            ),
            warnings=(),
        )