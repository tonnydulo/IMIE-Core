from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    MarketPhaseType,
    TradingContext,
    ValueAnalysis,
)
from imie.utils.analyst_ids import (
    ANALYST_VALUE,
)


@dataclass(frozen=True, slots=True)
class ValueAnalyst(Analyst):
    """
    Evaluates price location relative to VWAP fair value.

    Price below value is interpreted as institutional discount.
    Price above value is interpreted as institutional premium.
    """

    fair_value_tolerance_atr: float = 0.50

    def __post_init__(self) -> None:
        if self.fair_value_tolerance_atr < 0.0:
            raise ValueError(
                "fair_value_tolerance_atr cannot be negative."
            )

    def analyze(
        self,
        context: TradingContext,
    ) -> ValueAnalysis:
        if not isinstance(
            context,
            TradingContext,
        ):
            raise TypeError(
                "context must be a TradingContext."
            )

        measurements = context.measurements

        price = float(
            measurements.price
        )

        fair_value = measurements.vwap
        atr14 = measurements.atr14

        if fair_value is None:
            return self._unknown(
                price=price,
                warning="VWAP fair value is unavailable.",
            )

        distance = price - fair_value

        atr_distance = (
            distance / atr14
            if atr14 is not None
            and atr14 > 0.0
            else None
        )

        tolerance = self._calculate_tolerance(
            context
        )

        if abs(distance) <= tolerance:
            return ValueAnalysis(
                direction=InstitutionalDirection.NEUTRAL,
                value_state="FAIR_VALUE",
                market_phase=MarketPhaseType.COMPRESSION,
                price=price,
                fair_value=fair_value,
                distance_to_value=distance,
                atr_distance_to_value=atr_distance,
                confidence=75.0,
                opinion="Price is trading at fair value.",
                evidence=(
                    (
                        "Price is within the configured "
                        "VWAP fair-value tolerance."
                    ),
                    (
                        f"Price is {abs(distance):.2f} "
                        "from VWAP."
                    ),
                ),
                warnings=(),
            )

        if distance < 0.0:
            confidence = self._directional_confidence(
                atr_distance
            )

            return ValueAnalysis(
                direction=InstitutionalDirection.BULLISH,
                value_state="DISCOUNT",
                market_phase=MarketPhaseType.ACCUMULATION,
                price=price,
                fair_value=fair_value,
                distance_to_value=distance,
                atr_distance_to_value=atr_distance,
                confidence=confidence,
                opinion="Price is trading below fair value at discount.",
                evidence=(
                    "Price is trading below VWAP fair value.",
                    (
                        f"Price is {abs(distance):.2f} "
                        "below VWAP."
                    ),
                ),
                warnings=(
                    (
                        "Discount describes value location "
                        "and does not confirm an entry."
                    ),
                ),
            )

        confidence = self._directional_confidence(
            atr_distance
        )

        return ValueAnalysis(
            direction=InstitutionalDirection.BEARISH,
            value_state="PREMIUM",
            market_phase=MarketPhaseType.DISTRIBUTION,
            price=price,
            fair_value=fair_value,
            distance_to_value=distance,
            atr_distance_to_value=atr_distance,
            confidence=confidence,
            opinion="Price is trading above fair value at premium.",
            evidence=(
                "Price is trading above VWAP fair value.",
                (
                    f"Price is {distance:.2f} "
                    "above VWAP."
                ),
            ),
            warnings=(
                (
                    "Premium describes value location "
                    "and does not confirm an entry."
                ),
            ),
        )

    def analyze_result(
        self,
        context: TradingContext,
    ) -> AnalystResult:
        analysis = self.analyze(
            context
        )

        return AnalystResult(
            analyst="ValueAnalyst",
            analyst_id=ANALYST_VALUE,
            opinion=analysis.opinion,
            confidence=analysis.confidence,
            evidence=list(
                analysis.evidence
            ),
            warnings=list(
                analysis.warnings
            ),
            payload=analysis,
            enabled=True,
        )

    def _calculate_tolerance(
        self,
        context: TradingContext,
    ) -> float:
        measurements = context.measurements

        atr_tolerance = (
            measurements.atr14
            * self.fair_value_tolerance_atr
            if measurements.atr14 is not None
            and measurements.atr14 > 0.0
            else 0.0
        )

        configured_tolerance = (
            measurements.core_tolerance
            if measurements.core_tolerance is not None
            else 0.0
        )

        return max(
            atr_tolerance,
            configured_tolerance,
        )

    @staticmethod
    def _directional_confidence(
        atr_distance: float | None,
    ) -> float:
        if atr_distance is None:
            return 65.0

        return min(
            95.0,
            65.0
            + max(
                0.0,
                abs(atr_distance) - 0.50,
            ) * 10.0,
        )

    @staticmethod
    def _unknown(
        *,
        price: float,
        warning: str,
    ) -> ValueAnalysis:
        return ValueAnalysis(
            direction=InstitutionalDirection.UNKNOWN,
            value_state="UNKNOWN",
            market_phase=MarketPhaseType.UNKNOWN,
            price=price,
            fair_value=None,
            distance_to_value=None,
            atr_distance_to_value=None,
            confidence=0.0,
            opinion="Value context unavailable.",
            evidence=(),
            warnings=(
                warning,
            ),
        )