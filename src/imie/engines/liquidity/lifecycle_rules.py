from __future__ import annotations

from imie.models import LiquidityPoolStateType


LEGAL_TRANSITIONS: dict[
    LiquidityPoolStateType,
    frozenset[LiquidityPoolStateType],
] = {
    LiquidityPoolStateType.ACTIVE: frozenset(
        {
            LiquidityPoolStateType.ACTIVE,
            LiquidityPoolStateType.SWEPT,
        }
    ),
    LiquidityPoolStateType.SWEPT: frozenset(
        {
            LiquidityPoolStateType.SWEPT,
            LiquidityPoolStateType.RETESTED,
        }
    ),
    LiquidityPoolStateType.RETESTED: frozenset(
        {
            LiquidityPoolStateType.RETESTED,
            LiquidityPoolStateType.CONSUMED,
        }
    ),
    LiquidityPoolStateType.CONSUMED: frozenset(
        {
            LiquidityPoolStateType.CONSUMED,
            LiquidityPoolStateType.RETIRED,
        }
    ),
    LiquidityPoolStateType.RETIRED: frozenset(
        {
            LiquidityPoolStateType.RETIRED,
        }
    ),
}