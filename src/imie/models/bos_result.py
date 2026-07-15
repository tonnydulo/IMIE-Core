from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BosResult:
    """
    Result produced by BosEngine.

    Represents a completed-candle Break of Structure.
    """

    bullish_break: bool = False
    bearish_break: bool = False

    bullish_break_level: float | None = None
    bearish_break_level: float | None = None

    confirmation_price: float | None = None

    @property
    def detected(self) -> bool:
        return (
            self.bullish_break
            or self.bearish_break
        )