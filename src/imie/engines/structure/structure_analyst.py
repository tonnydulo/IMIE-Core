from __future__ import annotations

from dataclasses import replace

from imie.engines.structure.core import StructureEngine
from imie.models import (
    AnalystResult,
    MarketPhaseType,
    StructureResult,
    TradingContext,
)
from imie.utils.analyst_ids import ANALYST_STRUCTURE


class StructureAnalyst:
    """
    Coordinates structural market analysis.

    The detailed structural calculations are delegated to StructureEngine.
    """

    analyst_name = "StructureAnalyst"

    def __init__(
        self,
        *,
        left_bars: int = 2,
        right_bars: int = 2,
    ) -> None:
        self.engine = StructureEngine(
            left_bars=left_bars,
            right_bars=right_bars,
        )

    def analyze(
        self,
        context: TradingContext,
    ) -> AnalystResult:
        structure = self.engine.evaluate(
            context
        )

        structure = replace(
            structure,
            market_phase=self._resolve_market_phase(
                structure
            ),
        )

        return AnalystResult(
            analyst_id=ANALYST_STRUCTURE,
            analyst=self.analyst_name,
            opinion="STRUCTURE_READY",
            confidence=structure.confidence,
            evidence=list(
                structure.evidence
            ),
            warnings=list(
                structure.warnings
            ),
            payload=structure,
        )

    @staticmethod
    def _resolve_market_phase(
        structure: StructureResult,
    ) -> MarketPhaseType:
        if (
            structure.bullish_mss
            or structure.bearish_mss
            or structure.bullish_choch
            or structure.bearish_choch
        ):
            return MarketPhaseType.REVERSAL

        if (
            structure.bullish_break
            or structure.state
            == "BULLISH_STRUCTURE"
        ):
            return MarketPhaseType.MARKUP

        if (
            structure.bearish_break
            or structure.state
            == "BEARISH_STRUCTURE"
        ):
            return MarketPhaseType.MARKDOWN

        if (
            structure.state
            == "NEUTRAL_STRUCTURE"
        ):
            return MarketPhaseType.COMPRESSION

        return MarketPhaseType.UNKNOWN