from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    MarketBar,
    MarketPhaseType,
    PressureAnalysis,
    TradingContext,
)
from imie.utils.analyst_ids import (
    ANALYST_PRESSURE,
)


@dataclass(frozen=True, slots=True)
class PressureAnalyst(Analyst):
    """
    Evaluates short-term buying and selling pressure from
    completed market bars.

    This analyst does not calculate indicators. It consumes
    bars already present in TradingContext.
    """

    lookback: int = 5
    minimum_body_ratio: float = 0.35
    strong_close_location: float = 0.70
    dominance_threshold: float = 15.0

    def __post_init__(self) -> None:
        if self.lookback < 2:
            raise ValueError(
                "lookback must be at least 2."
            )

        if not 0.0 <= self.minimum_body_ratio <= 1.0:
            raise ValueError(
                "minimum_body_ratio must be between 0 and 1."
            )

        if not 0.0 <= self.strong_close_location <= 1.0:
            raise ValueError(
                "strong_close_location must be between 0 and 1."
            )

        if self.dominance_threshold < 0.0:
            raise ValueError(
                "dominance_threshold cannot be negative."
            )

    def analyze(
        self,
        context: TradingContext,
    ) -> PressureAnalysis:
        if not isinstance(
            context,
            TradingContext,
        ):
            raise TypeError(
                "context must be a TradingContext."
            )

        bars = tuple(
            context.snapshot.bars
        )

        if len(bars) < 2:
            return self._unknown(
                warning=(
                    "At least two completed bars are required "
                    "to evaluate pressure."
                )
            )

        recent_bars = bars[
            -min(
                self.lookback,
                len(bars),
            ):
        ]

        bullish_score = 0.0
        bearish_score = 0.0
        directional_count = 0

        bullish_closes = 0
        bearish_closes = 0

        for bar in recent_bars:
            bull, bear, directional = (
                self._score_bar(
                    bar
                )
            )

            bullish_score += bull
            bearish_score += bear

            if directional:
                directional_count += 1

            if bar.close > bar.open:
                bullish_closes += 1
            elif bar.close < bar.open:
                bearish_closes += 1

        evaluated_count = len(
            recent_bars
        )

        maximum_score = (
            evaluated_count * 100.0
        )

        bullish_percent = (
            bullish_score / maximum_score * 100.0
            if maximum_score > 0.0
            else 0.0
        )

        bearish_percent = (
            bearish_score / maximum_score * 100.0
            if maximum_score > 0.0
            else 0.0
        )

        latest = recent_bars[-1]

        exhaustion = self._resolve_exhaustion(
            latest=latest,
            bullish_closes=bullish_closes,
            bearish_closes=bearish_closes,
        )

        if exhaustion == "SELLING_EXHAUSTED":
            return PressureAnalysis(
                direction=InstitutionalDirection.BULLISH,
                pressure="SELLING_EXHAUSTED",
                market_phase=MarketPhaseType.REVERSAL,
                bullish_score=bullish_percent,
                bearish_score=bearish_percent,
                evaluated_bar_count=evaluated_count,
                directional_bar_count=directional_count,
                confidence=75.0,
                opinion="Selling pressure exhausted.",
                evidence=(
                    "Recent selling was rejected by a strong lower wick.",
                    "The latest candle closed away from its low.",
                ),
                warnings=(),
            )

        if exhaustion == "BUYING_EXHAUSTED":
            return PressureAnalysis(
                direction=InstitutionalDirection.BEARISH,
                pressure="BUYING_EXHAUSTED",
                market_phase=MarketPhaseType.REVERSAL,
                bullish_score=bullish_percent,
                bearish_score=bearish_percent,
                evaluated_bar_count=evaluated_count,
                directional_bar_count=directional_count,
                confidence=75.0,
                opinion="Buying pressure exhausted.",
                evidence=(
                    "Recent buying was rejected by a strong upper wick.",
                    "The latest candle closed away from its high.",
                ),
                warnings=(),
            )

        difference = (
            bullish_percent - bearish_percent
        )

        if difference >= self.dominance_threshold:
            confidence = min(
                95.0,
                60.0 + abs(difference),
            )

            return PressureAnalysis(
                direction=InstitutionalDirection.BULLISH,
                pressure="BUYING",
                market_phase=MarketPhaseType.EXPANSION,
                bullish_score=bullish_percent,
                bearish_score=bearish_percent,
                evaluated_bar_count=evaluated_count,
                directional_bar_count=directional_count,
                confidence=confidence,
                opinion="Buying pressure dominates.",
                evidence=(
                    (
                        f"Bullish pressure score is "
                        f"{bullish_percent:.1f}."
                    ),
                    (
                        f"{bullish_closes} of "
                        f"{evaluated_count} recent bars "
                        "closed bullish."
                    ),
                ),
                warnings=(),
            )

        if difference <= -self.dominance_threshold:
            confidence = min(
                95.0,
                60.0 + abs(difference),
            )

            return PressureAnalysis(
                direction=InstitutionalDirection.BEARISH,
                pressure="SELLING",
                market_phase=MarketPhaseType.EXPANSION,
                bullish_score=bullish_percent,
                bearish_score=bearish_percent,
                evaluated_bar_count=evaluated_count,
                directional_bar_count=directional_count,
                confidence=confidence,
                opinion="Selling pressure dominates.",
                evidence=(
                    (
                        f"Bearish pressure score is "
                        f"{bearish_percent:.1f}."
                    ),
                    (
                        f"{bearish_closes} of "
                        f"{evaluated_count} recent bars "
                        "closed bearish."
                    ),
                ),
                warnings=(),
            )

        return PressureAnalysis(
            direction=InstitutionalDirection.NEUTRAL,
            pressure="BALANCED",
            market_phase=MarketPhaseType.COMPRESSION,
            bullish_score=bullish_percent,
            bearish_score=bearish_percent,
            evaluated_bar_count=evaluated_count,
            directional_bar_count=directional_count,
            confidence=65.0,
            opinion="Buying and selling pressure remain balanced.",
            evidence=(
                (
                    f"Bullish pressure score is "
                    f"{bullish_percent:.1f}."
                ),
                (
                    f"Bearish pressure score is "
                    f"{bearish_percent:.1f}."
                ),
            ),
            warnings=(),
        )

    def analyze_result(
        self,
        context: TradingContext,
    ) -> AnalystResult:
        analysis = self.analyze(
            context
        )

        return AnalystResult(
            analyst="PressureAnalyst",
            analyst_id=ANALYST_PRESSURE,
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

    def _score_bar(
        self,
        bar: MarketBar,
    ) -> tuple[
        float,
        float,
        bool,
    ]:
        candle_range = bar.range

        if candle_range <= 0.0:
            return (
                0.0,
                0.0,
                False,
            )

        body_size = abs(
            bar.close - bar.open
        )

        body_ratio = (
            body_size / candle_range
        )

        if body_ratio < self.minimum_body_ratio:
            return (
                0.0,
                0.0,
                False,
            )

        bullish_close_location = (
            bar.close - bar.low
        ) / candle_range

        bearish_close_location = (
            bar.high - bar.close
        ) / candle_range

        base_score = (
            body_ratio * 60.0
        )

        if bar.close > bar.open:
            close_bonus = (
                40.0
                if bullish_close_location
                >= self.strong_close_location
                else 20.0
            )

            return (
                min(
                    100.0,
                    base_score + close_bonus,
                ),
                0.0,
                True,
            )

        if bar.close < bar.open:
            close_bonus = (
                40.0
                if bearish_close_location
                >= self.strong_close_location
                else 20.0
            )

            return (
                0.0,
                min(
                    100.0,
                    base_score + close_bonus,
                ),
                True,
            )

        return (
            0.0,
            0.0,
            False,
        )

    @staticmethod
    def _resolve_exhaustion(
        *,
        latest: MarketBar,
        bullish_closes: int,
        bearish_closes: int,
    ) -> str | None:
        candle_range = latest.range

        if candle_range <= 0.0:
            return None

        body_high = max(
            latest.open,
            latest.close,
        )

        body_low = min(
            latest.open,
            latest.close,
        )

        upper_wick = (
            latest.high - body_high
        )

        lower_wick = (
            body_low - latest.low
        )

        upper_wick_ratio = (
            upper_wick / candle_range
        )

        lower_wick_ratio = (
            lower_wick / candle_range
        )

        close_location = (
            latest.close - latest.low
        ) / candle_range

        if (
            bearish_closes >= 3
            and lower_wick_ratio >= 0.45
            and close_location >= 0.60
        ):
            return "SELLING_EXHAUSTED"

        if (
            bullish_closes >= 3
            and upper_wick_ratio >= 0.45
            and close_location <= 0.40
        ):
            return "BUYING_EXHAUSTED"

        return None

    @staticmethod
    def _unknown(
        *,
        warning: str,
    ) -> PressureAnalysis:
        return PressureAnalysis(
            direction=InstitutionalDirection.UNKNOWN,
            pressure="UNKNOWN",
            market_phase=MarketPhaseType.UNKNOWN,
            bullish_score=0.0,
            bearish_score=0.0,
            evaluated_bar_count=0,
            directional_bar_count=0,
            confidence=0.0,
            opinion="Pressure context unavailable.",
            evidence=(),
            warnings=(
                warning,
            ),
        )