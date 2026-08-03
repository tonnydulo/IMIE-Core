from __future__ import annotations

from imie.models import (
    ChochResult,
    MssResult,
)


class MssEngine:
    """
    Interprets Change of Character as a Market Structure Shift.

    Bullish MSS:
        bullish CHoCH confirmed

    Bearish MSS:
        bearish CHoCH confirmed

    MSS does not inspect candles or swings directly. It consumes the
    typed result produced by ChochEngine.
    """

    def evaluate(
        self,
        *,
        choch: ChochResult,
    ) -> MssResult:
        if choch.bullish_choch:
            return MssResult(
                bullish_mss=True,
                bearish_mss=False,
                confidence=90.0,
                reason=(
                    "Bullish Market Structure Shift confirmed after "
                    "a bullish Change of Character."
                ),
            )

        if choch.bearish_choch:
            return MssResult(
                bullish_mss=False,
                bearish_mss=True,
                confidence=90.0,
                reason=(
                    "Bearish Market Structure Shift confirmed after "
                    "a bearish Change of Character."
                ),
            )

        return MssResult(
            bullish_mss=False,
            bearish_mss=False,
            confidence=0.0,
            reason=(
                "No Market Structure Shift was confirmed because "
                "Change of Character is absent."
            ),
        )