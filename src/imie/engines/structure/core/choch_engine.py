from __future__ import annotations

from imie.models import ChochResult


class ChochEngine:
    """
    Detects Change of Character from established directional structure.

    Bullish CHoCH:
        Prior bearish structure plus bullish BOS.

    Bearish CHoCH:
        Prior bullish structure plus bearish BOS.

    Neutral or unconfirmed structure cannot produce CHoCH.
    """

    def evaluate(
        self,
        *,
        structure_direction: str,
        bullish_break: bool,
        bearish_break: bool,
    ) -> ChochResult:
        """
        Return a typed ChochResult.
        """

        normalized_direction = (
            str(structure_direction)
            .strip()
            .lower()
        )

        bullish_choch = (
            normalized_direction == "short"
            and bullish_break
            and not bearish_break
        )

        bearish_choch = (
            normalized_direction == "long"
            and bearish_break
            and not bullish_break
        )

        return ChochResult(
            bullish_choch=bullish_choch,
            bearish_choch=bearish_choch,
        )