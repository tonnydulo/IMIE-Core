from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    MarketPhaseType,
    ParticipationAnalysis,
    PressureAnalysis,
    TradingContext,
)
from imie.utils.analyst_ids import (
    ANALYST_PARTICIPATION,
)


@dataclass(frozen=True, slots=True)
class ParticipationAnalyst(Analyst):
    """
    Evaluates whether recent volume confirms directional pressure.

    Strong volume is only directional when the Pressure analyst
    provides a bullish or bearish direction.
    """

    baseline_lookback: int = 20
    recent_lookback: int = 5
    strong_volume_ratio: float = 1.20
    weak_volume_ratio: float = 0.75

    def __post_init__(self) -> None:
        if self.baseline_lookback < 5:
            raise ValueError(
                "baseline_lookback must be at least 5."
            )

        if self.recent_lookback < 2:
            raise ValueError(
                "recent_lookback must be at least 2."
            )

        if self.recent_lookback > self.baseline_lookback:
            raise ValueError(
                "recent_lookback cannot exceed "
                "baseline_lookback."
            )

        if self.strong_volume_ratio <= 1.0:
            raise ValueError(
                "strong_volume_ratio must be greater than 1."
            )

        if not 0.0 < self.weak_volume_ratio < 1.0:
            raise ValueError(
                "weak_volume_ratio must be between 0 and 1."
            )

    def analyze(
        self,
        context: TradingContext,
        pressure_result: AnalystResult,
    ) -> ParticipationAnalysis:
        self._validate_inputs(
            context=context,
            pressure_result=pressure_result,
        )

        bars = tuple(
            context.snapshot.bars
        )

        if len(bars) < self.recent_lookback:
            return self._unknown(
                warning=(
                    "Insufficient completed bars to evaluate "
                    "market participation."
                )
            )

        evaluated_bars = bars[
            -min(
                self.baseline_lookback,
                len(bars),
            ):
        ]

        recent_bars = evaluated_bars[
            -self.recent_lookback:
        ]

        average_volume = (
            sum(
                bar.volume
                for bar in evaluated_bars
            )
            / len(evaluated_bars)
        )

        recent_average_volume = (
            sum(
                bar.volume
                for bar in recent_bars
            )
            / len(recent_bars)
        )

        volume_ratio = (
            recent_average_volume / average_volume
            if average_volume > 0.0
            else 0.0
        )

        pressure_direction = (
            self._pressure_direction(
                pressure_result
            )
        )

        if volume_ratio >= self.strong_volume_ratio:
            if (
                pressure_direction
                is InstitutionalDirection.BULLISH
            ):
                return ParticipationAnalysis(
                    direction=InstitutionalDirection.BULLISH,
                    participation="BULLISH",
                    market_phase=MarketPhaseType.EXPANSION,
                    average_volume=average_volume,
                    recent_average_volume=recent_average_volume,
                    volume_ratio=volume_ratio,
                    evaluated_bar_count=len(evaluated_bars),
                    recent_bar_count=len(recent_bars),
                    confidence=self._strong_confidence(
                        volume_ratio
                    ),
                    opinion=(
                        "Participation supports buyers."
                    ),
                    evidence=(
                        (
                            "Recent volume is "
                            f"{volume_ratio:.2f} times "
                            "the baseline average."
                        ),
                        (
                            "Directional pressure and volume "
                            "both support buyers."
                        ),
                    ),
                    warnings=(),
                )

            if (
                pressure_direction
                is InstitutionalDirection.BEARISH
            ):
                return ParticipationAnalysis(
                    direction=InstitutionalDirection.BEARISH,
                    participation="BEARISH",
                    market_phase=MarketPhaseType.EXPANSION,
                    average_volume=average_volume,
                    recent_average_volume=recent_average_volume,
                    volume_ratio=volume_ratio,
                    evaluated_bar_count=len(evaluated_bars),
                    recent_bar_count=len(recent_bars),
                    confidence=self._strong_confidence(
                        volume_ratio
                    ),
                    opinion=(
                        "Participation supports sellers."
                    ),
                    evidence=(
                        (
                            "Recent volume is "
                            f"{volume_ratio:.2f} times "
                            "the baseline average."
                        ),
                        (
                            "Directional pressure and volume "
                            "both support sellers."
                        ),
                    ),
                    warnings=(),
                )

            return ParticipationAnalysis(
                direction=InstitutionalDirection.NEUTRAL,
                participation="STRONG_NON_DIRECTIONAL",
                market_phase=MarketPhaseType.TRANSITION,
                average_volume=average_volume,
                recent_average_volume=recent_average_volume,
                volume_ratio=volume_ratio,
                evaluated_bar_count=len(evaluated_bars),
                recent_bar_count=len(recent_bars),
                confidence=70.0,
                opinion=(
                    "Strong participation remains "
                    "non-directional."
                ),
                evidence=(
                    (
                        "Recent volume is "
                        f"{volume_ratio:.2f} times "
                        "the baseline average."
                    ),
                    (
                        "Pressure does not provide a confirmed "
                        "directional advantage."
                    ),
                ),
                warnings=(),
            )

        if volume_ratio <= self.weak_volume_ratio:
            return ParticipationAnalysis(
                direction=InstitutionalDirection.NEUTRAL,
                participation="WEAK",
                market_phase=MarketPhaseType.COMPRESSION,
                average_volume=average_volume,
                recent_average_volume=recent_average_volume,
                volume_ratio=volume_ratio,
                evaluated_bar_count=len(evaluated_bars),
                recent_bar_count=len(recent_bars),
                confidence=65.0,
                opinion="Weak participation is non-directional.",
                evidence=(
                    (
                        "Recent volume is only "
                        f"{volume_ratio:.2f} times "
                        "the baseline average."
                    ),
                ),
                warnings=(
                    "Directional moves may lack participation.",
                ),
            )

        return ParticipationAnalysis(
            direction=InstitutionalDirection.NEUTRAL,
            participation="NORMAL",
            market_phase=MarketPhaseType.TRANSITION,
            average_volume=average_volume,
            recent_average_volume=recent_average_volume,
            volume_ratio=volume_ratio,
            evaluated_bar_count=len(evaluated_bars),
            recent_bar_count=len(recent_bars),
            confidence=60.0,
            opinion=(
                "Participation is normal and "
                "non-directional."
            ),
            evidence=(
                (
                    "Recent volume is "
                    f"{volume_ratio:.2f} times "
                    "the baseline average."
                ),
            ),
            warnings=(),
        )

    def analyze_result(
        self,
        context: TradingContext,
        pressure_result: AnalystResult,
    ) -> AnalystResult:
        analysis = self.analyze(
            context=context,
            pressure_result=pressure_result,
        )

        return AnalystResult(
            analyst="ParticipationAnalyst",
            analyst_id=ANALYST_PARTICIPATION,
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

    @staticmethod
    def _pressure_direction(
        pressure_result: AnalystResult,
    ) -> InstitutionalDirection:
        payload = pressure_result.payload

        if isinstance(
            payload,
            PressureAnalysis,
        ):
            return payload.direction

        opinion = (
            pressure_result
            .opinion
            .strip()
            .upper()
        )

        if "BUYING PRESSURE" in opinion:
            return InstitutionalDirection.BULLISH

        if "SELLING PRESSURE" in opinion:
            return InstitutionalDirection.BEARISH

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _strong_confidence(
        volume_ratio: float,
    ) -> float:
        return min(
            95.0,
            70.0
            + max(
                0.0,
                volume_ratio - 1.0,
            ) * 25.0,
        )

    @staticmethod
    def _validate_inputs(
        *,
        context: TradingContext,
        pressure_result: AnalystResult,
    ) -> None:
        if not isinstance(
            context,
            TradingContext,
        ):
            raise TypeError(
                "context must be a TradingContext."
            )

        if not isinstance(
            pressure_result,
            AnalystResult,
        ):
            raise TypeError(
                "pressure_result must be an AnalystResult."
            )

    @staticmethod
    def _unknown(
        *,
        warning: str,
    ) -> ParticipationAnalysis:
        return ParticipationAnalysis(
            direction=InstitutionalDirection.UNKNOWN,
            participation="UNKNOWN",
            market_phase=MarketPhaseType.UNKNOWN,
            average_volume=0.0,
            recent_average_volume=0.0,
            volume_ratio=0.0,
            evaluated_bar_count=0,
            recent_bar_count=0,
            confidence=0.0,
            opinion="Participation context unavailable.",
            evidence=(),
            warnings=(
                warning,
            ),
        )