from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_pool import LiquidityPool
from imie.models.liquidity_types import (
    LiquidityPoolStateType,
)


@dataclass(frozen=True, slots=True)
class LiquidityPoolState:
    """
    Immutable runtime state of a liquidity pool.

    LiquidityPool describes the institutional liquidity.

    LiquidityPoolState describes the lifecycle of that
    liquidity through time.
    """

    pool: LiquidityPool

    state: LiquidityPoolStateType

    created_bar: int

    updated_bar: int

    sweep_count: int

    retest_count: int

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    def __post_init__(self) -> None:

        if not isinstance(
            self.pool,
            LiquidityPool,
        ):
            raise TypeError(
                "pool must be a LiquidityPool."
            )

        if not isinstance(
            self.state,
            LiquidityPoolStateType,
        ):
            raise TypeError(
                "state must be a "
                "LiquidityPoolStateType."
            )

        if self.created_bar < 0:
            raise ValueError(
                "created_bar cannot be negative."
            )

        if self.updated_bar < self.created_bar:
            raise ValueError(
                "updated_bar cannot precede "
                "created_bar."
            )

        if self.sweep_count < 0:
            raise ValueError(
                "sweep_count cannot be negative."
            )

        if self.retest_count < 0:
            raise ValueError(
                "retest_count cannot be negative."
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

    @property
    def age(self) -> int:
        return (
            self.updated_bar
            - self.created_bar
        )

    @property
    def is_active(self) -> bool:
        return (
            self.state
            is LiquidityPoolStateType.ACTIVE
        )

    @property
    def is_swept(self) -> bool:
        return (
            self.state
            is LiquidityPoolStateType.SWEPT
        )

    @property
    def is_retested(self) -> bool:
        return (
            self.state
            is LiquidityPoolStateType.RETESTED
        )

    @property
    def is_consumed(self) -> bool:
        return (
            self.state
            is LiquidityPoolStateType.CONSUMED
        )

    @property
    def is_retired(self) -> bool:
        return (
            self.state
            is LiquidityPoolStateType.RETIRED
        )