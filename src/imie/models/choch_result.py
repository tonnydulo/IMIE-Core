from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChochResult:
    """
    Result produced by ChochEngine.
    """

    bullish_choch: bool = False
    bearish_choch: bool = False

    @property
    def detected(self) -> bool:
        return (
            self.bullish_choch
            or self.bearish_choch
        )