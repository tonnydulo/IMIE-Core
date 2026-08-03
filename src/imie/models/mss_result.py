from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MssResult:
    """
    Result produced by MssEngine.

    A Market Structure Shift represents a confirmed change in
    directional market control after Change of Character.
    """

    bullish_mss: bool = False
    bearish_mss: bool = False

    confidence: float = 0.0
    reason: str = ""

    def __post_init__(self) -> None:
        confidence = max(
            0.0,
            min(100.0, float(self.confidence)),
        )

        reason = self.reason.strip()

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

        if self.bullish_mss and self.bearish_mss:
            raise ValueError(
                "MssResult cannot confirm bullish and bearish "
                "MSS simultaneously."
            )

    @property
    def detected(self) -> bool:
        return (
            self.bullish_mss
            or self.bearish_mss
        )