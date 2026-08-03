from __future__ import annotations

from dataclasses import dataclass

from imie.engines.order_blocks.order_block_candidate import (
    OrderBlockCandidate,
)
from imie.models import (
    OrderBlockFinding,
    OrderBlockOrigin,
    OrderBlockSide,
    StructureResult,
)


@dataclass(frozen=True, slots=True)
class OrderBlockBuilder:
    """
    Builds validated OrderBlockFinding objects from qualified
    OrderBlockCandidate objects and completed structure results.

    The builder owns:

    - origin resolution;
    - confidence calculation;
    - displacement normalization;
    - reason generation;
    - evidence generation.

    It performs no market search and no lifecycle management.
    """

    def build_bullish(
        self,
        *,
        candidate: OrderBlockCandidate,
        structure: StructureResult,
    ) -> OrderBlockFinding:
        self._validate_inputs(
            candidate=candidate,
            structure=structure,
        )

        if not self._has_bullish_confirmation(
            structure
        ):
            raise ValueError(
                "A bullish structure confirmation is required."
            )

        origin = self._resolve_bullish_origin(
            structure
        )

        confidence = self._calculate_confidence(
            candidate=candidate,
            structure=structure,
        )

        displacement = max(
            0.0,
            (
                candidate.displacement_bar.close
                - candidate.source_bar.high
            ),
        )

        return OrderBlockFinding(
            upper=candidate.source_bar.high,
            lower=candidate.source_bar.low,
            side=OrderBlockSide.BULLISH,
            origin=origin,
            source_bar_index=candidate.source_index,
            displacement=round(
                displacement,
                6,
            ),
            strength=round(
                candidate.displacement_score,
                2,
            ),
            confidence=confidence,
            reason=(
                "A bearish source candle preceded qualified bullish "
                "displacement and completed bullish structural "
                "confirmation."
            ),
            evidence=self._build_bullish_evidence(
                candidate=candidate,
                origin=origin,
            ),
            detector=self.__class__.__name__,
        )

    @staticmethod
    def _validate_inputs(
        *,
        candidate: OrderBlockCandidate,
        structure: StructureResult,
    ) -> None:
        if not isinstance(
            candidate,
            OrderBlockCandidate,
        ):
            raise TypeError(
                "candidate must be an OrderBlockCandidate."
            )

        if not isinstance(
            structure,
            StructureResult,
        ):
            raise TypeError(
                "structure must be a StructureResult."
            )

    @staticmethod
    def _has_bullish_confirmation(
        structure: StructureResult,
    ) -> bool:
        return (
            structure.bullish_break
            or structure.bullish_choch
            or structure.bullish_mss
        )

    @staticmethod
    def _resolve_bullish_origin(
        structure: StructureResult,
    ) -> OrderBlockOrigin:
        if structure.bullish_mss:
            return OrderBlockOrigin.MSS

        if structure.bullish_choch:
            return OrderBlockOrigin.CHOCH

        if structure.bullish_break:
            return OrderBlockOrigin.BOS

        return OrderBlockOrigin.UNCLASSIFIED

    @staticmethod
    def _calculate_confidence(
        *,
        candidate: OrderBlockCandidate,
        structure: StructureResult,
    ) -> float:
        if structure.bullish_mss:
            structure_score = 100.0
        elif structure.bullish_choch:
            structure_score = 90.0
        elif structure.bullish_break:
            structure_score = 80.0
        else:
            structure_score = 0.0

        confidence = (
            candidate.displacement_score * 0.70
            + structure_score * 0.30
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            ),
            2,
        )

    @staticmethod
    def _build_bullish_evidence(
        *,
        candidate: OrderBlockCandidate,
        origin: OrderBlockOrigin,
    ) -> tuple[str, ...]:
        source = candidate.source_bar
        displacement = candidate.displacement_bar

        return (
            (
                "The source candle closed bearish from "
                f"{source.open:.4f} to {source.close:.4f}."
            ),
            (
                "The displacement candle closed bullish from "
                f"{displacement.open:.4f} to "
                f"{displacement.close:.4f}."
            ),
            (
                "The displacement candle closed above the source "
                f"high of {source.high:.4f}."
            ),
            (
                "Bullish structure confirmation was supplied by "
                f"{origin.value}."
            ),
            (
                "The qualified candidate originated at source "
                f"bar index {candidate.source_index}."
            ),
        )