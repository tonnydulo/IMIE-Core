from __future__ import annotations

from typing import Protocol

from imie.models.liquidity_finding import LiquidityFinding
from imie.models.swing import Swing


class LiquidityDetector(Protocol):
    """
    Common contract implemented by liquidity detectors.

    Liquidity detectors consume previously confirmed structural
    observations and return immutable LiquidityFinding objects.

    Detectors do not build liquidity pools, rank targets,
    create narratives, or make trading decisions.
    """

    def detect(
        self,
        swings: tuple[Swing, ...],
    ) -> tuple[LiquidityFinding, ...]:
        """
        Detect liquidity from confirmed market swings.

        Args:
            swings:
                Confirmed Swing objects produced by the
                Structure subsystem.

        Returns:
            An immutable tuple of liquidity findings.
        """
        ...