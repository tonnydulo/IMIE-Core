from __future__ import annotations

from dataclasses import dataclass

from imie.models.order_block_types import (
    OrderBlockImportance,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockState,
)


@dataclass(frozen=True, slots=True)
class OrderBlock:
    """
    Immutable institutional order-block definition.

    An OrderBlock represents a confirmed price range associated
    with institutional displacement or a meaningful structural
    event.

    The model records what the block is. Detection, lifecycle
    transitions, mitigation, invalidation, and trade decisions
    belong to separate engines.
    """

    upper: float
    lower: float

    side: OrderBlockSide
    origin: OrderBlockOrigin
    state: OrderBlockState

    source_bar_index: int
    created_bar_index: int

    strength: float
    confidence: float

    reason: str
    evidence: tuple[str, ...]
    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.side,
            OrderBlockSide,
        ):
            raise TypeError(
                "OrderBlock side must be an OrderBlockSide."
            )

        if not isinstance(
            self.origin,
            OrderBlockOrigin,
        ):
            raise TypeError(
                "OrderBlock origin must be an OrderBlockOrigin."
            )

        if not isinstance(
            self.state,
            OrderBlockState,
        ):
            raise TypeError(
                "OrderBlock state must be an OrderBlockState."
            )

        if self.upper <= 0.0:
            raise ValueError(
                "OrderBlock upper must be positive."
            )

        if self.lower <= 0.0:
            raise ValueError(
                "OrderBlock lower must be positive."
            )

        if self.upper < self.lower:
            raise ValueError(
                "OrderBlock upper cannot be below lower."
            )

        if self.source_bar_index < 0:
            raise ValueError(
                "OrderBlock source_bar_index cannot be negative."
            )

        if self.created_bar_index < self.source_bar_index:
            raise ValueError(
                "OrderBlock created_bar_index cannot be earlier "
                "than source_bar_index."
            )

        if self.strength < 0.0:
            raise ValueError(
                "OrderBlock strength cannot be negative."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "OrderBlock confidence must be between 0 and 100."
            )

        if not isinstance(
            self.reason,
            str,
        ) or not self.reason.strip():
            raise ValueError(
                "OrderBlock reason cannot be empty."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "OrderBlock evidence entries must be "
                "non-empty strings."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.warnings
        ):
            raise ValueError(
                "OrderBlock warning entries must be "
                "non-empty strings."
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

    @property
    def is_active(self) -> bool:
        return self.state is OrderBlockState.ACTIVE

    @property
    def is_tested(self) -> bool:
        return self.state is OrderBlockState.TESTED

    @property
    def is_mitigated(self) -> bool:
        return self.state is OrderBlockState.MITIGATED

    @property
    def is_broken(self) -> bool:
        return self.state is OrderBlockState.BROKEN

    @property
    def is_retired(self) -> bool:
        return self.state is OrderBlockState.RETIRED

    @property
    def is_major(self) -> bool:
        return (
            self.importance
            is OrderBlockImportance.MAJOR
        )

    @property
    def importance(self) -> OrderBlockImportance:
        """
        Derive institutional importance from strength.

        Version 1 thresholds:

        - strength >= 80: MAJOR
        - strength >= 50: INTERMEDIATE
        - otherwise: MINOR

        Importance can later become an explicit field if additional
        contextual factors make that necessary.
        """
        if self.strength >= 80.0:
            return OrderBlockImportance.MAJOR

        if self.strength >= 50.0:
            return OrderBlockImportance.INTERMEDIATE

        return OrderBlockImportance.MINOR