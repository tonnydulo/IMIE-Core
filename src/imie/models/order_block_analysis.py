from __future__ import annotations

from dataclasses import dataclass, field

from imie.models import (
    OrderBlockFinding,
    OrderBlockLifecycleState,
)


@dataclass(frozen=True, slots=True)
class OrderBlockAnalysis:
    """
    Institutional interpretation of all known order blocks.

    This model does not detect order blocks and does not
    update lifecycle state. It summarizes the current
    institutional landscape for higher-level analysts.
    """

    nearest_bullish_block: (
        OrderBlockLifecycleState | None
    )

    nearest_bearish_block: (
        OrderBlockLifecycleState | None
    )

    strongest_block: (
        OrderBlockLifecycleState | None
    )

    active_blocks: tuple[
        OrderBlockLifecycleState,
        ...
    ] = field(default_factory=tuple)

    tested_blocks: tuple[
        OrderBlockLifecycleState,
        ...
    ] = field(default_factory=tuple)

    mitigated_blocks: tuple[
        OrderBlockLifecycleState,
        ...
    ] = field(default_factory=tuple)

    invalidated_blocks: tuple[
        OrderBlockLifecycleState,
        ...
    ] = field(default_factory=tuple)

    confidence: float = 0.0

    opinion: str = ""

    evidence: tuple[str, ...] = field(
        default_factory=tuple
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:

        confidence = max(
            0.0,
            min(
                100.0,
                float(self.confidence),
            ),
        )

        opinion = self.opinion.strip()

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "opinion",
            opinion,
        )

        object.__setattr__(
            self,
            "evidence",
            self._clean(
                self.evidence
            ),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean(
                self.warnings
            ),
        )

        self._validate_state(
            self.nearest_bullish_block
        )

        self._validate_state(
            self.nearest_bearish_block
        )

        self._validate_state(
            self.strongest_block
        )

        self._validate_collection(
            self.active_blocks
        )

        self._validate_collection(
            self.tested_blocks
        )

        self._validate_collection(
            self.mitigated_blocks
        )

        self._validate_collection(
            self.invalidated_blocks
        )

    @staticmethod
    def _validate_state(
        state: OrderBlockLifecycleState | None,
    ) -> None:

        if state is None:
            return

        if not isinstance(
            state,
            OrderBlockLifecycleState,
        ):
            raise TypeError(
                "Expected OrderBlockLifecycleState."
            )

    @classmethod
    def _validate_collection(
        cls,
        collection: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> None:

        for state in collection:
            cls._validate_state(state)

    @staticmethod
    def _clean(
        items: tuple[str, ...],
    ) -> tuple[str, ...]:

        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:

            text = str(item).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return tuple(cleaned)

    @property
    def active_count(self) -> int:
        return len(
            self.active_blocks
        )

    @property
    def tested_count(self) -> int:
        return len(
            self.tested_blocks
        )

    @property
    def mitigated_count(self) -> int:
        return len(
            self.mitigated_blocks
        )

    @property
    def invalidated_count(self) -> int:
        return len(
            self.invalidated_blocks
        )

    @property
    def has_active_blocks(self) -> bool:
        return self.active_count > 0

    @property
    def has_bullish_block(self) -> bool:
        return (
            self.nearest_bullish_block
            is not None
        )

    @property
    def has_bearish_block(self) -> bool:
        return (
            self.nearest_bearish_block
            is not None
        )

    @property
    def has_strongest_block(self) -> bool:
        return (
            self.strongest_block
            is not None
        )