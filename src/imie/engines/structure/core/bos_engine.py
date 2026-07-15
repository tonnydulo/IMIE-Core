from __future__ import annotations

from collections.abc import Sequence

from imie.models import (
    BosResult,
    MarketBar,
    Swing,
)


class BosEngine:
    """
    Detects completed-candle Break of Structure events.

    Bullish BOS:
        The latest completed candle closes above the most recent
        confirmed swing high.

    Bearish BOS:
        The latest completed candle closes below the most recent
        confirmed swing low.

    Wick-only breaks are ignored.
    """

    def evaluate(
        self,
        *,
        bars: Sequence[MarketBar],
        highs: Sequence[Swing],
        lows: Sequence[Swing],
    ) -> BosResult:
        """
        Return a typed BosResult.

        BosEngine never returns raw tuples.
        """

        if not bars:
            return BosResult()

        latest_close = float(bars[-1].close)

        latest_high = self._latest_swing(
            swings=highs,
            kind="HIGH",
        )

        latest_low = self._latest_swing(
            swings=lows,
            kind="LOW",
        )

        bullish_break = (
            latest_high is not None
            and latest_close > latest_high.price
        )

        bearish_break = (
            latest_low is not None
            and latest_close < latest_low.price
        )

        if bullish_break:
            return BosResult(
                bullish_break=True,
                bearish_break=False,
                bullish_break_level=float(
                    latest_high.price
                ),
                bearish_break_level=None,
                confirmation_price=latest_close,
            )

        if bearish_break:
            return BosResult(
                bullish_break=False,
                bearish_break=True,
                bullish_break_level=None,
                bearish_break_level=float(
                    latest_low.price
                ),
                confirmation_price=latest_close,
            )

        return BosResult()

    @staticmethod
    def _latest_swing(
        *,
        swings: Sequence[Swing],
        kind: str,
    ) -> Swing | None:
        matching_swings = [
            swing
            for swing in swings
            if swing.kind == kind
        ]

        if not matching_swings:
            return None

        return max(
            matching_swings,
            key=lambda swing: swing.index,
        )