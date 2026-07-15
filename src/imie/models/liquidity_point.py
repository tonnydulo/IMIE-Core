from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_types import LiquiditySide


@dataclass(frozen=True, slots=True)
class LiquidityPoint:
    """
    Represents one confirmed liquidity location.

    A point records the price and observations that confirmed
    resting buy-side or sell-side liquidity.

    Higher-level classification such as liquidity type,
    importance, confidence, lifecycle, and institutional
    location belongs to LiquidityFinding or LiquidityPool.
    """

    price: float

    side: LiquiditySide

    first_index: int
    second_index: int

    strength: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.side, LiquiditySide):
            raise TypeError(
                "LiquidityPoint side must be a LiquiditySide."
            )

        if self.price <= 0.0:
            raise ValueError(
                "LiquidityPoint price must be positive."
            )

        if self.first_index < 0:
            raise ValueError(
                "LiquidityPoint first_index cannot be negative."
            )

        if self.second_index < 0:
            raise ValueError(
                "LiquidityPoint second_index cannot be negative."
            )

        if self.second_index <= self.first_index:
            raise ValueError(
                "LiquidityPoint second_index must be greater "
                "than first_index."
            )

        if self.strength < 1:
            raise ValueError(
                "LiquidityPoint strength must be positive."
            )

    @property
    def kind(self) -> str:
        """
        Return the legacy uppercase side name.

        This compatibility property allows older diagnostic
        and display code to continue reading point.kind.
        """
        return self.side.name

    @property
    def is_buy_side(self) -> bool:
        """Return True when liquidity rests above price."""

        return self.side is LiquiditySide.BUY_SIDE

    @property
    def is_sell_side(self) -> bool:
        """Return True when liquidity rests below price."""

        return self.side is LiquiditySide.SELL_SIDE