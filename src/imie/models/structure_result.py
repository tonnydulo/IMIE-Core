from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.swing import Swing

@dataclass(frozen=True, slots=True)
class StructureResult:
    """
    Detailed market-structure assessment produced by StructureAnalyst.

    StructureResult describes structural information only. It does not
    authorize trades and does not modify a TradePlan.
    """

    symbol: str
    direction: str
    state: str
    confidence: float

    nearest_support: float | None
    nearest_resistance: float | None

    structural_target: float | None
    structural_stop: float | None

    projected_reward: float | None
    projected_risk: float | None
    projected_rr: float | None

    swing_high_count: int
    swing_low_count: int

    swings: tuple[Swing, ...] = field(default_factory=tuple)

    bullish_break: bool = False
    bearish_break: bool = False

    bullish_break_level: float | None = None
    bearish_break_level: float | None = None
    break_confirmation_price: float | None = None

    bullish_choch: bool = False
    bearish_choch: bool = False

    bullish_mss: bool = False
    bearish_mss: bool = False

    mss_confidence: float = 0.0
    mss_reason: str = ""

    evidence: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    reason: str = ""

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        direction = self.direction.strip().lower()
        state = self.state.strip().upper()
        reason = self.reason.strip()

        if not symbol:
            raise ValueError(
                "StructureResult symbol cannot be empty."
            )

        if direction not in {
            "long",
            "short",
            "neutral",
        }:
            raise ValueError(
                "StructureResult direction must be long, short, "
                "or neutral."
            )

        if not state:
            raise ValueError(
                "StructureResult state cannot be empty."
            )

        confidence = max(
            0.0,
            min(100.0, float(self.confidence)),
        )

        mss_confidence = max(
            0.0,
            min(100.0, float(self.mss_confidence)),
        )

        mss_reason = self.mss_reason.strip()

        swing_high_count = max(
            0,
            int(self.swing_high_count),
        )

        swing_low_count = max(
            0,
            int(self.swing_low_count),
        )

        for swing in self.swings:
            if not isinstance(
                swing,
                Swing,
            ):
                raise TypeError(
                    "StructureResult swings must contain "
                    "Swing objects."
                )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        object.__setattr__(
            self,
            "state",
            state,
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "mss_confidence",
            mss_confidence,
        )

        object.__setattr__(
            self,
            "mss_reason",
            mss_reason,
        )

        object.__setattr__(
            self,
            "swing_high_count",
            swing_high_count,
        )

        object.__setattr__(
            self,
            "swing_low_count",
            swing_low_count,
        )

        object.__setattr__(
            self,
            "evidence",
            self._clean_items(self.evidence),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(self.warnings),
        )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

        object.__setattr__(
            self,
            "swings",
            tuple(self.swings),
        )

        if self.bullish_break and self.bearish_break:
            raise ValueError(
                "StructureResult cannot confirm bullish and bearish "
                "breaks simultaneously."
            )

        if self.bullish_choch and self.bearish_choch:
            raise ValueError(
                "StructureResult cannot confirm bullish and bearish "
                "CHoCH simultaneously."
            )
        
        if self.bullish_mss and self.bearish_mss:
            raise ValueError(
                "StructureResult cannot confirm bullish and bearish "
                "MSS simultaneously."
            )

        if self.bullish_mss and not self.bullish_choch:
            raise ValueError(
                "Bullish MSS requires bullish CHoCH."
            )

        if self.bearish_mss and not self.bearish_choch:
            raise ValueError(
                "Bearish MSS requires bearish CHoCH."
            )

        if self.bullish_choch and not self.bullish_break:
            raise ValueError(
                "Bullish CHoCH requires a bullish structural break."
            )

        if self.bearish_choch and not self.bearish_break:
            raise ValueError(
                "Bearish CHoCH requires a bearish structural break."
            )

        if self.bullish_break and self.bullish_break_level is None:
            raise ValueError(
                "A bullish break must include its broken swing-high level."
            )

        if self.bearish_break and self.bearish_break_level is None:
            raise ValueError(
                "A bearish break must include its broken swing-low level."
            )

        if (
            self.bullish_break or self.bearish_break
        ) and self.break_confirmation_price is None:
            raise ValueError(
                "A confirmed structural break must include the "
                "completed candle close."
            )

        if (
            self.projected_risk is not None
            and self.projected_risk < 0
        ):
            raise ValueError(
                "Projected structural risk cannot be negative."
            )

        if (
            self.projected_reward is not None
            and self.projected_reward < 0
        ):
            raise ValueError(
                "Projected structural reward cannot be negative."
            )

        if (
            self.projected_rr is not None
            and self.projected_rr < 0
        ):
            raise ValueError(
                "Projected structural RR cannot be negative."
            )

    @staticmethod
    def _clean_items(
        items: tuple[str, ...],
    ) -> tuple[str, ...]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(item).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return tuple(cleaned)