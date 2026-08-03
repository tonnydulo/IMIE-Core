from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    OrderBlockAnalysis,
    OrderBlockLifecycleState,
    OrderBlockSide,
    OrderBlockStateType,
)


@dataclass(frozen=True, slots=True)
class OrderBlockAnalyst(Analyst):
    """
    Produces an institutional interpretation of the current
    order-block landscape.

    The analyst consumes completed lifecycle states only.

    It does not:

    - detect order blocks;
    - score displacement;
    - build findings;
    - update lifecycle state;
    - authorize trades.
    """

    def analyze(
        self,
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> OrderBlockAnalysis:
        self._validate_inputs(
            states
        )

        active_blocks = tuple(
            state
            for state in states
            if state.state
            in {
                OrderBlockStateType.NEW,
                OrderBlockStateType.ACTIVE,
            }
        )

        tested_blocks = tuple(
            state
            for state in states
            if state.state
            is OrderBlockStateType.TESTED
        )

        mitigated_blocks = tuple(
            state
            for state in states
            if state.state
            is OrderBlockStateType.MITIGATED
        )

        invalidated_blocks = tuple(
            state
            for state in states
            if state.state
            is OrderBlockStateType.INVALIDATED
        )

        actionable_blocks = (
            active_blocks
            + tested_blocks
            + mitigated_blocks
        )

        nearest_bullish = self._nearest_bullish(
            actionable_blocks
        )

        nearest_bearish = self._nearest_bearish(
            actionable_blocks
        )

        strongest = self._strongest_block(
            actionable_blocks
        )

        confidence = self._calculate_confidence(
            actionable_blocks=actionable_blocks,
            strongest=strongest,
        )

        opinion = self._build_opinion(
            nearest_bullish=nearest_bullish,
            nearest_bearish=nearest_bearish,
        )

        evidence = self._build_evidence(
            active_blocks=active_blocks,
            tested_blocks=tested_blocks,
            mitigated_blocks=mitigated_blocks,
            invalidated_blocks=invalidated_blocks,
            strongest=strongest,
            nearest_bullish=nearest_bullish,
            nearest_bearish=nearest_bearish,
        )

        warnings = self._build_warnings(
            actionable_blocks=actionable_blocks,
            nearest_bullish=nearest_bullish,
            nearest_bearish=nearest_bearish,
        )

        return OrderBlockAnalysis(
            nearest_bullish_block=nearest_bullish,
            nearest_bearish_block=nearest_bearish,
            strongest_block=strongest,
            active_blocks=active_blocks,
            tested_blocks=tested_blocks,
            mitigated_blocks=mitigated_blocks,
            invalidated_blocks=invalidated_blocks,
            confidence=confidence,
            opinion=opinion,
            evidence=evidence,
            warnings=warnings,
        )

    def analyze_result(
        self,
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> AnalystResult:
        """
        Produce the standard analyst envelope consumed by
        AnalystRegistry and DecisionDirector.
        """
        analysis = self.analyze(
            states
        )

        return AnalystResult(
            analyst=self.__class__.__name__,
            analyst_id="ORDER_BLOCK",
            opinion=analysis.opinion,
            confidence=analysis.confidence,
            evidence=list(
                analysis.evidence
            ),
            warnings=list(
                analysis.warnings
            ),
            payload=analysis,
            enabled=True,
        )

    @staticmethod
    def _validate_inputs(
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> None:
        if not isinstance(
            states,
            tuple,
        ):
            raise TypeError(
                "states must be a tuple of "
                "OrderBlockLifecycleState objects."
            )

        for state in states:
            if not isinstance(
                state,
                OrderBlockLifecycleState,
            ):
                raise TypeError(
                    "states must contain "
                    "OrderBlockLifecycleState objects."
                )

    @staticmethod
    def _nearest_bullish(
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> OrderBlockLifecycleState | None:
        bullish = tuple(
            state
            for state in states
            if state.finding.side
            is OrderBlockSide.BULLISH
        )

        if not bullish:
            return None

        return min(
            bullish,
            key=lambda state: (
                state.finding.upper,
                state.finding.lower,
            ),
        )

    @staticmethod
    def _nearest_bearish(
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> OrderBlockLifecycleState | None:
        bearish = tuple(
            state
            for state in states
            if state.finding.side
            is OrderBlockSide.BEARISH
        )

        if not bearish:
            return None

        return min(
            bearish,
            key=lambda state: (
                state.finding.lower,
                state.finding.upper,
            ),
        )

    @staticmethod
    def _strongest_block(
        states: tuple[
            OrderBlockLifecycleState,
            ...
        ],
    ) -> OrderBlockLifecycleState | None:
        if not states:
            return None

        return max(
            states,
            key=lambda state: (
                state.finding.confidence,
                state.finding.strength,
            ),
        )

    @staticmethod
    def _calculate_confidence(
        *,
        actionable_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        strongest: (
            OrderBlockLifecycleState
            | None
        ),
    ) -> float:
        if not actionable_blocks:
            return 0.0

        if strongest is None:
            return 60.0

        strongest_confidence = (
            strongest.finding.confidence
        )

        if strongest_confidence >= 95.0:
            return 95.0

        if strongest_confidence >= 90.0:
            return 90.0

        if len(actionable_blocks) >= 2:
            return 80.0

        return 60.0

    @staticmethod
    def _build_opinion(
        *,
        nearest_bullish: (
            OrderBlockLifecycleState
            | None
        ),
        nearest_bearish: (
            OrderBlockLifecycleState
            | None
        ),
    ) -> str:
        if (
            nearest_bullish is not None
            and nearest_bearish is None
        ):
            return (
                "Active institutional demand remains "
                "below price."
            )

        if (
            nearest_bearish is not None
            and nearest_bullish is None
        ):
            return (
                "Active institutional supply remains "
                "above price."
            )

        if (
            nearest_bullish is not None
            and nearest_bearish is not None
        ):
            return (
                "Institutional order flow remains balanced."
            )

        return (
            "No actionable institutional order blocks."
        )

    @staticmethod
    def _build_evidence(
        *,
        active_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        tested_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        mitigated_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        invalidated_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        strongest: (
            OrderBlockLifecycleState
            | None
        ),
        nearest_bullish: (
            OrderBlockLifecycleState
            | None
        ),
        nearest_bearish: (
            OrderBlockLifecycleState
            | None
        ),
    ) -> tuple[str, ...]:
        evidence: list[str] = []

        if active_blocks:
            evidence.append(
                f"{len(active_blocks)} active institutional "
                f"order block"
                f"{'' if len(active_blocks) == 1 else 's'}."
            )

        if tested_blocks:
            evidence.append(
                f"{len(tested_blocks)} tested order block"
                f"{'' if len(tested_blocks) == 1 else 's'}."
            )

        if mitigated_blocks:
            evidence.append(
                f"{len(mitigated_blocks)} mitigated order block"
                f"{'' if len(mitigated_blocks) == 1 else 's'}."
            )

        if invalidated_blocks:
            evidence.append(
                f"{len(invalidated_blocks)} invalidated order block"
                f"{'' if len(invalidated_blocks) == 1 else 's'}."
            )

        if strongest is not None:
            evidence.append(
                "Strongest order block confidence is "
                f"{strongest.finding.confidence:.0f}%."
            )

        if nearest_bullish is not None:
            evidence.append(
                "Nearest institutional demand block spans "
                f"{nearest_bullish.finding.lower:.4f} to "
                f"{nearest_bullish.finding.upper:.4f}."
            )

        if nearest_bearish is not None:
            evidence.append(
                "Nearest institutional supply block spans "
                f"{nearest_bearish.finding.lower:.4f} to "
                f"{nearest_bearish.finding.upper:.4f}."
            )

        if not evidence:
            evidence.append(
                "No institutional order blocks are currently "
                "available."
            )

        return OrderBlockAnalyst._clean_items(
            evidence
        )

    @staticmethod
    def _build_warnings(
        *,
        actionable_blocks: tuple[
            OrderBlockLifecycleState,
            ...
        ],
        nearest_bullish: (
            OrderBlockLifecycleState
            | None
        ),
        nearest_bearish: (
            OrderBlockLifecycleState
            | None
        ),
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if not actionable_blocks:
            warnings.append(
                "No active order blocks are available."
            )

        if nearest_bullish is None:
            warnings.append(
                "No institutional demand block is available."
            )

        if nearest_bearish is None:
            warnings.append(
                "No institutional supply block is available."
            )

        return OrderBlockAnalyst._clean_items(
            warnings
        )

    @staticmethod
    def _clean_items(
        items: list[str],
    ) -> tuple[str, ...]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(
                item
            ).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return tuple(cleaned)