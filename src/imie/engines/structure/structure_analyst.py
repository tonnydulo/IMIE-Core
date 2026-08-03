from __future__ import annotations

from imie.engines.structure.core import StructureEngine
from imie.models import (
    AnalystResult,
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
        structure = self.engine.evaluate(context)

        return AnalystResult(
            analyst_id=ANALYST_STRUCTURE,
            analyst=self.analyst_name,
            opinion="STRUCTURE_READY",
            confidence=structure.confidence,
            evidence=list(structure.evidence),
            warnings=list(structure.warnings),
            payload=structure,
        )