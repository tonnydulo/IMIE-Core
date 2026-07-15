from __future__ import annotations

from imie.engines.structure.core.bos_engine import BosEngine
from imie.engines.structure.core.choch_engine import ChochEngine
from imie.engines.structure.swing_detector import SwingDetector
from imie.engines.structure.core.mss_engine import MssEngine
from imie.models import (
    StructureResult,
    Swing,
    TradingContext,
)


class StructureEngine:
    """
    Core engine responsible for structural market analysis.

    Current responsibilities:

    - detect confirmed swing highs and lows;
    - identify nearest structural support and resistance;
    - infer bullish, bearish, neutral, or unconfirmed structure;
    - detect completed-candle Break of Structure;
    - detect Change of Character;
    - build explainable evidence, warnings, and reasons;
    - return StructureResult.

    Future responsibilities:

    - Market Structure Shift (MSS)
    - Internal Structure
    - External Structure
    - Liquidity Structure
    - Structural Targets
    """

    def __init__(
        self,
        *,
        left_bars: int = 2,
        right_bars: int = 2,
    ) -> None:
        self.detector = SwingDetector(
            left_bars=left_bars,
            right_bars=right_bars,
        )

        self.bos_engine = BosEngine()
        self.choch_engine = ChochEngine()
        self.mss_engine = MssEngine()

    def evaluate(
        self,
        context: TradingContext,
    ) -> StructureResult:
        bars = context.snapshot.bars
        price = context.measurements.price
        symbol = context.snapshot.symbol

        swings = self.detector.detect(bars)

        highs = [
            swing
            for swing in swings
            if swing.kind == "HIGH"
        ]

        lows = [
            swing
            for swing in swings
            if swing.kind == "LOW"
        ]

        nearest_support = self._nearest_support(
            swings=lows,
            current_price=price,
        )

        nearest_resistance = self._nearest_resistance(
            swings=highs,
            current_price=price,
        )

        direction, state, confidence = self._infer_structure(
            highs=highs,
            lows=lows,
        )

        bos = self.bos_engine.evaluate(
            bars=bars,
            highs=highs,
            lows=lows,
        )

        choch = self.choch_engine.evaluate(
            structure_direction=direction,
            bullish_break=bos.bullish_break,
            bearish_break=bos.bearish_break,
        )

        evidence = self._build_evidence(
            highs=highs,
            lows=lows,
            direction=direction,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
        )

        mss = self.mss_engine.evaluate(
            choch=choch,
        )

        if bos.bullish_break:
            evidence = (
                *evidence,
                (
                    "Bullish Break of Structure confirmed above "
                    f"{bos.bullish_break_level:.2f} by a completed "
                    f"close at {bos.confirmation_price:.2f}."
                ),
            )

        if bos.bearish_break:
            evidence = (
                *evidence,
                (
                    "Bearish Break of Structure confirmed below "
                    f"{bos.bearish_break_level:.2f} by a completed "
                    f"close at {bos.confirmation_price:.2f}."
                ),
            )

        if choch.bullish_choch:
            evidence = (
                *evidence,
                (
                    "Bullish Change of Character confirmed because "
                    "price broke above structure while the established "
                    "structure was bearish."
                ),
            )

        if choch.bearish_choch:
            evidence = (
                *evidence,
                (
                    "Bearish Change of Character confirmed because "
                    "price broke below structure while the established "
                    "structure was bullish."
                ),
            )

        if mss.bullish_mss:
            evidence = (
                 *evidence,
                (
                    "Bullish Market Structure Shift confirms that "
                    "institutional control has likely transitioned "
                    "from sellers to buyers."
                ),
            )

        if mss.bearish_mss:
            evidence = (
                *evidence,
                (
                    "Bearish Market Structure Shift confirms that "
                    "institutional control has likely transitioned "
                    "from buyers to sellers."
                ),
            )

        warnings = self._build_warnings(
            highs=highs,
            lows=lows,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
        )

        return StructureResult(
            symbol=symbol,
            direction=direction,
            state=state,
            confidence=confidence,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            structural_target=None,
            structural_stop=None,
            projected_reward=None,
            projected_risk=None,
            projected_rr=None,
            swing_high_count=len(highs),
            swing_low_count=len(lows),
            bullish_break=bos.bullish_break,
            bearish_break=bos.bearish_break,
            bullish_break_level=bos.bullish_break_level,
            bearish_break_level=bos.bearish_break_level,
            break_confirmation_price=bos.confirmation_price,
            bullish_choch=choch.bullish_choch,
            bearish_choch=choch.bearish_choch,
            bullish_mss=mss.bullish_mss,
            bearish_mss=mss.bearish_mss,
            mss_confidence=mss.confidence,
            mss_reason=mss.reason,
            evidence=evidence,
            warnings=warnings,
            reason=self._build_reason(
                direction=direction,
                state=state,
                bullish_choch=choch.bullish_choch,
                bearish_choch=choch.bearish_choch,
                bullish_mss=mss.bullish_mss,
                bearish_mss=mss.bearish_mss,
            ),
        )

    @staticmethod
    def _infer_structure(
        *,
        highs: list[Swing],
        lows: list[Swing],
    ) -> tuple[str, str, float]:
        if len(highs) < 2 or len(lows) < 2:
            return (
                "neutral",
                "UNCONFIRMED_STRUCTURE",
                40.0,
            )

        previous_high = highs[-2].price
        latest_high = highs[-1].price

        previous_low = lows[-2].price
        latest_low = lows[-1].price

        higher_high = latest_high > previous_high
        lower_high = latest_high < previous_high

        higher_low = latest_low > previous_low
        lower_low = latest_low < previous_low

        if higher_high and higher_low:
            return (
                "long",
                "BULLISH_STRUCTURE",
                85.0,
            )

        if lower_high and lower_low:
            return (
                "short",
                "BEARISH_STRUCTURE",
                85.0,
            )

        return (
            "neutral",
            "NEUTRAL_STRUCTURE",
            60.0,
        )

    @staticmethod
    def _nearest_support(
        *,
        swings: list[Swing],
        current_price: float,
    ) -> float | None:
        levels_below_price = [
            swing.price
            for swing in swings
            if swing.price <= current_price
        ]

        if not levels_below_price:
            return None

        return max(levels_below_price)

    @staticmethod
    def _nearest_resistance(
        *,
        swings: list[Swing],
        current_price: float,
    ) -> float | None:
        levels_above_price = [
            swing.price
            for swing in swings
            if swing.price >= current_price
        ]

        if not levels_above_price:
            return None

        return min(levels_above_price)

    @staticmethod
    def _build_evidence(
        *,
        highs: list[Swing],
        lows: list[Swing],
        direction: str,
        nearest_support: float | None,
        nearest_resistance: float | None,
    ) -> tuple[str, ...]:
        evidence: list[str] = [
            f"{len(highs)} confirmed swing highs.",
            f"{len(lows)} confirmed swing lows.",
        ]

        if len(highs) >= 2:
            previous_high = highs[-2].price
            latest_high = highs[-1].price

            if latest_high > previous_high:
                evidence.append(
                    "The latest confirmed swing high is higher than "
                    "the previous swing high."
                )
            elif latest_high < previous_high:
                evidence.append(
                    "The latest confirmed swing high is lower than "
                    "the previous swing high."
                )
            else:
                evidence.append(
                    "The two latest confirmed swing highs are equal."
                )

        if len(lows) >= 2:
            previous_low = lows[-2].price
            latest_low = lows[-1].price

            if latest_low > previous_low:
                evidence.append(
                    "The latest confirmed swing low is higher than "
                    "the previous swing low."
                )
            elif latest_low < previous_low:
                evidence.append(
                    "The latest confirmed swing low is lower than "
                    "the previous swing low."
                )
            else:
                evidence.append(
                    "The two latest confirmed swing lows are equal."
                )

        if direction == "long":
            evidence.append(
                "Higher-high and higher-low progression confirms "
                "bullish structure."
            )
        elif direction == "short":
            evidence.append(
                "Lower-high and lower-low progression confirms "
                "bearish structure."
            )
        else:
            evidence.append(
                "Confirmed swings do not currently establish a "
                "directional structure."
            )

        if nearest_support is not None:
            evidence.append(
                f"Nearest confirmed structural support is "
                f"{nearest_support:.2f}."
            )

        if nearest_resistance is not None:
            evidence.append(
                f"Nearest confirmed structural resistance is "
                f"{nearest_resistance:.2f}."
            )

        return tuple(evidence)

    @staticmethod
    def _build_warnings(
        *,
        highs: list[Swing],
        lows: list[Swing],
        nearest_support: float | None,
        nearest_resistance: float | None,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if len(highs) < 2:
            warnings.append(
                "At least two confirmed swing highs are required "
                "for directional structure."
            )

        if len(lows) < 2:
            warnings.append(
                "At least two confirmed swing lows are required "
                "for directional structure."
            )

        if nearest_support is None:
            warnings.append(
                "No confirmed structural support was found below "
                "the current price."
            )

        if nearest_resistance is None:
            warnings.append(
                "No confirmed structural resistance was found above "
                "the current price."
            )

        return tuple(warnings)

    @staticmethod
    def _build_reason(
        *,
        direction: str,
        state: str,
        bullish_choch: bool,
        bearish_choch: bool,
        bullish_mss: bool,
        bearish_mss: bool,
    ) -> str:
        
        if bullish_mss:
            return (
                "Bullish Market Structure Shift confirms that "
                "institutional control has transitioned from "
                "sellers to buyers."
            )

        if bearish_mss:
            return (
                "Bearish Market Structure Shift confirms that "
                "institutional control has transitioned from "
                "buyers to sellers."
            )

        if bullish_choch:
            return (
                "Bullish Change of Character suggests control may be "
                "shifting from sellers to buyers."
            )

        if bearish_choch:
            return (
                "Bearish Change of Character suggests control may be "
                "shifting from buyers to sellers."
            )

        if direction == "long":
            return (
                "Bullish market structure was confirmed from higher "
                "swing highs and higher swing lows."
            )

        if direction == "short":
            return (
                "Bearish market structure was confirmed from lower "
                "swing highs and lower swing lows."
            )

        if state == "UNCONFIRMED_STRUCTURE":
            return (
                "There are not enough confirmed swings to establish "
                "directional market structure."
            )

        return (
            "Swing progression is mixed, so market structure is neutral."
        )