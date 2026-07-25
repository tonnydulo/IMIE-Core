from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    AuctionAnalysis,
    InstitutionalDirection,
    MarketPhaseType,
    TradingContext,
)
from imie.utils.analyst_ids import (
    ANALYST_AUCTION,
)


@dataclass(frozen=True, slots=True)
class AuctionAnalyst(Analyst):
    """
    Interprets price location relative to VWAP together with
    the existing trend opinion.

    The analyst does not calculate indicators. It consumes
    completed TradingContext measurements and TrendAnalyst output.
    """

    vwap_tolerance_atr: float = 0.20

    def __post_init__(self) -> None:
        if self.vwap_tolerance_atr < 0.0:
            raise ValueError(
                "vwap_tolerance_atr cannot be negative."
            )

    def analyze(
        self,
        context: TradingContext,
        trend: AnalystResult,
    ) -> AuctionAnalysis:
        self._validate_inputs(
            context=context,
            trend=trend,
        )

        measurements = context.measurements
        price = measurements.price
        vwap = measurements.vwap
        atr14 = measurements.atr14

        if vwap is None:
            return AuctionAnalysis(
                direction=InstitutionalDirection.UNKNOWN,
                control="UNKNOWN",
                market_phase=MarketPhaseType.UNKNOWN,
                price=price,
                vwap=None,
                distance_to_vwap=None,
                atr_distance_to_vwap=None,
                confidence=0.0,
                opinion="Auction context unavailable.",
                evidence=(),
                warnings=(
                    "VWAP is unavailable.",
                ),
            )

        distance = price - vwap

        atr_distance = (
            distance / atr14
            if atr14 is not None
            and atr14 > 0.0
            else None
        )

        tolerance = self._calculate_tolerance(
            context=context,
        )

        trend_direction = self._trend_direction(
            trend
        )

        if abs(distance) <= tolerance:
            return AuctionAnalysis(
                direction=InstitutionalDirection.NEUTRAL,
                control="BALANCED",
                market_phase=MarketPhaseType.COMPRESSION,
                price=price,
                vwap=vwap,
                distance_to_vwap=distance,
                atr_distance_to_vwap=atr_distance,
                confidence=70.0,
                opinion="Auction remains balanced near VWAP.",
                evidence=(
                    (
                        "Price is trading within the "
                        "VWAP auction tolerance."
                    ),
                    (
                        f"Price is {abs(distance):.2f} "
                        "from VWAP."
                    ),
                ),
                warnings=(),
            )

        if (
            distance > 0.0
            and trend_direction
            is InstitutionalDirection.BULLISH
        ):
            return AuctionAnalysis(
                direction=InstitutionalDirection.BULLISH,
                control="BUYERS",
                market_phase=MarketPhaseType.MARKUP,
                price=price,
                vwap=vwap,
                distance_to_vwap=distance,
                atr_distance_to_vwap=atr_distance,
                confidence=85.0,
                opinion="Buyers control the auction.",
                evidence=(
                    "Price is trading above VWAP.",
                    (
                        "Trend direction supports "
                        "higher-price acceptance."
                    ),
                ),
                warnings=(),
            )

        if (
            distance < 0.0
            and trend_direction
            is InstitutionalDirection.BEARISH
        ):
            return AuctionAnalysis(
                direction=InstitutionalDirection.BEARISH,
                control="SELLERS",
                market_phase=MarketPhaseType.MARKDOWN,
                price=price,
                vwap=vwap,
                distance_to_vwap=distance,
                atr_distance_to_vwap=atr_distance,
                confidence=85.0,
                opinion="Sellers control the auction.",
                evidence=(
                    "Price is trading below VWAP.",
                    (
                        "Trend direction supports "
                        "lower-price acceptance."
                    ),
                ),
                warnings=(),
            )

        return AuctionAnalysis(
            direction=InstitutionalDirection.UNKNOWN,
            control="UNRESOLVED",
            market_phase=MarketPhaseType.TRANSITION,
            price=price,
            vwap=vwap,
            distance_to_vwap=distance,
            atr_distance_to_vwap=atr_distance,
            confidence=55.0,
            opinion="Auction direction is unresolved.",
            evidence=(
                (
                    "Price location relative to VWAP "
                    "conflicts with trend direction."
                ),
            ),
            warnings=(
                (
                    "Auction control requires confirmation "
                    "before directional use."
                ),
            ),
        )

    def analyze_result(
        self,
        context: TradingContext,
        trend: AnalystResult,
    ) -> AnalystResult:
        analysis = self.analyze(
            context=context,
            trend=trend,
        )

        return AnalystResult(
            analyst="AuctionAnalyst",
            analyst_id=ANALYST_AUCTION,
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
        *,
        context: TradingContext,
    ) -> float:
        measurements = context.measurements

        atr_tolerance = (
            measurements.atr14
            * self.vwap_tolerance_atr
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
    def _trend_direction(
        trend: AnalystResult,
    ) -> InstitutionalDirection:
        opinion = trend.opinion.strip().upper()

        if "BULLISH" in opinion:
            return InstitutionalDirection.BULLISH

        if "BEARISH" in opinion:
            return InstitutionalDirection.BEARISH

        if (
            "NEUTRAL" in opinion
            or "BALANCED" in opinion
        ):
            return InstitutionalDirection.NEUTRAL

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _validate_inputs(
        *,
        context: TradingContext,
        trend: AnalystResult,
    ) -> None:
        if not isinstance(
            context,
            TradingContext,
        ):
            raise TypeError(
                "context must be a TradingContext."
            )

        if not isinstance(
            trend,
            AnalystResult,
        ):
            raise TypeError(
                "trend must be an AnalystResult."
            )