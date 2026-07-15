from __future__ import annotations

from dataclasses import dataclass

from imie.models.order_block import OrderBlock
from imie.models.order_block_types import (
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockState,
)


@dataclass(frozen=True, slots=True)
class OrderBlockFinding:
    """
    Raw output produced by an OrderBlockDetector.

    A finding represents a candidate institutional order block
    before validation, filtering, clustering, or lifecycle
    processing.

    Findings are promoted into immutable OrderBlock objects
    only after passing builder validation.
    """

    upper: float
    lower: float

    side: OrderBlockSide
    origin: OrderBlockOrigin

    source_bar_index: int

    displacement: float
    strength: float
    confidence: float

    reason: str
    evidence: tuple[str, ...]

    detector: str

    def __post_init__(self) -> None:

        if not isinstance(
            self.side,
            OrderBlockSide,
        ):
            raise TypeError(
                "OrderBlockFinding side must be an OrderBlockSide."
            )

        if not isinstance(
            self.origin,
            OrderBlockOrigin,
        ):
            raise TypeError(
                "OrderBlockFinding origin must be an OrderBlockOrigin."
            )

        if self.upper <= 0.0:
            raise ValueError(
                "OrderBlockFinding upper must be positive."
            )

        if self.lower <= 0.0:
            raise ValueError(
                "OrderBlockFinding lower must be positive."
            )

        if self.upper < self.lower:
            raise ValueError(
                "OrderBlockFinding upper cannot be below lower."
            )

        if self.source_bar_index < 0:
            raise ValueError(
                "OrderBlockFinding source_bar_index cannot be negative."
            )

        if self.displacement < 0.0:
            raise ValueError(
                "OrderBlockFinding displacement cannot be negative."
            )

        if self.strength < 0.0:
            raise ValueError(
                "OrderBlockFinding strength cannot be negative."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "OrderBlockFinding confidence must be between 0 and 100."
            )

        if not self.reason.strip():
            raise ValueError(
                "OrderBlockFinding reason cannot be empty."
            )

        if not self.detector.strip():
            raise ValueError(
                "OrderBlockFinding detector cannot be empty."
            )

        if any(
            not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "OrderBlockFinding evidence entries cannot be empty."
            )

    @property
    def midpoint(self) -> float:
        return (
            self.upper + self.lower
        ) / 2.0

    @property
    def height(self) -> float:
        return self.upper - self.lower

    @property
    def is_bullish(self) -> bool:
        return self.side is OrderBlockSide.BULLISH

    @property
    def is_bearish(self) -> bool:
        return self.side is OrderBlockSide.BEARISH

    def to_order_block(
        self,
    ) -> OrderBlock:
        """
        Promote this validated finding into an immutable
        institutional OrderBlock.

        The caller is responsible for ensuring that the
        finding has passed all builder validation before
        promotion.
        """

        return OrderBlock(
            upper=self.upper,
            lower=self.lower,
            side=self.side,
            origin=self.origin,
            state=OrderBlockState.ACTIVE,
            source_bar_index=self.source_bar_index,
            created_bar_index=self.source_bar_index,
            strength=self.strength,
            confidence=self.confidence,
            reason=self.reason,
            evidence=self.evidence,
            warnings=(),
        )