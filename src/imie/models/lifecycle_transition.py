from __future__ import annotations

from dataclasses import dataclass

from imie.models import LiquidityPoolStateType


@dataclass(frozen=True, slots=True)
class LifecycleTransition:
    """
    One immutable lifecycle transition.

    Produced by business rules.
    Applied by LiquidityLifecycleEngine.
    """

    previous: LiquidityPoolStateType

    current: LiquidityPoolStateType

    reason: str

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    def __post_init__(self) -> None:

        if not isinstance(
            self.previous,
            LiquidityPoolStateType,
        ):
            raise TypeError(
                "previous must be LiquidityPoolStateType."
            )

        if not isinstance(
            self.current,
            LiquidityPoolStateType,
        ):
            raise TypeError(
                "current must be LiquidityPoolStateType."
            )

        if not self.reason.strip():
            raise ValueError(
                "reason cannot be empty."
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