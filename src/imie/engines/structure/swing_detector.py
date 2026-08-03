from __future__ import annotations

from collections.abc import Sequence

from imie.models.market_bar import MarketBar
from imie.models.swing import Swing


class SwingDetector:
    """
    Detects confirmed swing highs and swing lows from completed bars.

    A swing high must be higher than every bar within the configured
    number of bars on both its left and right.

    A swing low must be lower than every bar within the configured
    number of bars on both its left and right.

    Because right-side confirmation is required, the newest bars cannot
    be reported as confirmed swings until enough later bars exist.
    """

    def __init__(
        self,
        *,
        left_bars: int = 2,
        right_bars: int = 2,
    ) -> None:
        if left_bars < 1:
            raise ValueError(
                "left_bars must be at least 1."
            )

        if right_bars < 1:
            raise ValueError(
                "right_bars must be at least 1."
            )

        self.left_bars = left_bars
        self.right_bars = right_bars

    def detect(
        self,
        bars: Sequence[MarketBar],
    ) -> tuple[Swing, ...]:
        """
        Return confirmed swings in chronological order.
        """

        minimum_bars = (
            self.left_bars
            + self.right_bars
            + 1
        )

        if len(bars) < minimum_bars:
            return ()

        swings: list[Swing] = []

        first_candidate = self.left_bars
        last_candidate = len(bars) - self.right_bars

        for index in range(
            first_candidate,
            last_candidate,
        ):
            candidate = bars[index]

            left_window = bars[
                index - self.left_bars:index
            ]

            right_window = bars[
                index + 1:index + self.right_bars + 1
            ]

            if self._is_swing_high(
                candidate=candidate,
                left_window=left_window,
                right_window=right_window,
            ):
                swings.append(
                    Swing(
                        index=index,
                        price=float(candidate.high),
                        kind="HIGH",
                        strength=min(
                            self.left_bars,
                            self.right_bars,
                        ),
                    )
                )

            if self._is_swing_low(
                candidate=candidate,
                left_window=left_window,
                right_window=right_window,
            ):
                swings.append(
                    Swing(
                        index=index,
                        price=float(candidate.low),
                        kind="LOW",
                        strength=min(
                            self.left_bars,
                            self.right_bars,
                        ),
                    )
                )

        return tuple(swings)

    def detect_highs(
        self,
        bars: Sequence[MarketBar],
    ) -> tuple[Swing, ...]:
        return tuple(
            swing
            for swing in self.detect(bars)
            if swing.kind == "HIGH"
        )

    def detect_lows(
        self,
        bars: Sequence[MarketBar],
    ) -> tuple[Swing, ...]:
        return tuple(
            swing
            for swing in self.detect(bars)
            if swing.kind == "LOW"
        )

    def _is_swing_high(
        self,
        *,
        candidate: MarketBar,
        left_window: Sequence[MarketBar],
        right_window: Sequence[MarketBar],
    ) -> bool:
        neighboring_highs = (
            bar.high
            for bar in (
                *left_window,
                *right_window,
            )
        )

        return all(
            candidate.high > high
            for high in neighboring_highs
        )

    def _is_swing_low(
        self,
        *,
        candidate: MarketBar,
        left_window: Sequence[MarketBar],
        right_window: Sequence[MarketBar],
    ) -> bool:
        neighboring_lows = (
            bar.low
            for bar in (
                *left_window,
                *right_window,
            )
        )

        return all(
            candidate.low < low
            for low in neighboring_lows
        )