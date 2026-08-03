from imie.models import (
    AcceptanceResult,
    AnalystResult,
    SetupLifecycle,
    TradingContext,
)
from imie.utils.constants import (
    ACCEPTANCE_EXCEPTIONAL,
    ACCEPTANCE_GOOD,
    ACCEPTANCE_NONE,
    ACCEPTANCE_STRONG,
    LIFECYCLE_AT_CORE,
)


class AcceptanceAnalyst:
    analyst_name = "AcceptanceAnalyst"

    def analyze_result(
        self,
        context: TradingContext,
        lifecycle: SetupLifecycle,
    ) -> AnalystResult:
        """
        Return the standardized analyst contract.

        The detailed AcceptanceResult remains available in payload.
        """

        acceptance = self.analyze(
            context=context,
            lifecycle=lifecycle,
        )

        evidence = list(acceptance.evidence)

        if acceptance.reason:
            evidence.append(acceptance.reason)

        warnings = list(acceptance.warnings)

        if not acceptance.accepted and not warnings:
            warnings.append(
                "Completed-candle acceptance has not been confirmed."
            )

        return AnalystResult(
            analyst=self.analyst_name,
            opinion=acceptance.level,
            confidence=float(acceptance.confidence),
            evidence=evidence,
            warnings=warnings,
            payload=acceptance,
        )

    def analyze(
        self,
        context: TradingContext,
        lifecycle: SetupLifecycle,
    ) -> AcceptanceResult:
        """
        Evaluate completed-candle acceptance at Core.

        This original interface is preserved for compatibility with
        existing services, tests, and the console pipeline.
        """

        symbol = context.snapshot.symbol
        bars = context.snapshot.bars

        if lifecycle.state != LIFECYCLE_AT_CORE:
            return AcceptanceResult(
                symbol=symbol,
                accepted=False,
                direction=lifecycle.direction,
                level=ACCEPTANCE_NONE,
                score=0,
                confidence=0.0,
                trigger_price=None,
                previous_level=None,
                pullback_low=None,
                pullback_high=None,
                reason=(
                    "Acceptance is evaluated only when price is at Core."
                ),
            )

        if len(bars) < 2:
            return AcceptanceResult(
                symbol=symbol,
                accepted=False,
                direction=lifecycle.direction,
                level=ACCEPTANCE_NONE,
                score=0,
                confidence=0.0,
                trigger_price=None,
                previous_level=None,
                pullback_low=None,
                pullback_high=None,
                warnings=[
                    "At least two completed bars are required."
                ],
                reason="Insufficient completed candles.",
            )

        previous_bar = bars[-2]
        current_bar = bars[-1]
        atr14 = context.measurements.atr14

        if lifecycle.direction == "long":
            return self._analyze_long(
                symbol=symbol,
                previous_bar=previous_bar,
                current_bar=current_bar,
                atr14=atr14,
            )

        if lifecycle.direction == "short":
            return self._analyze_short(
                symbol=symbol,
                previous_bar=previous_bar,
                current_bar=current_bar,
                atr14=atr14,
            )

        return AcceptanceResult(
            symbol=symbol,
            accepted=False,
            direction=lifecycle.direction,
            level=ACCEPTANCE_NONE,
            score=0,
            confidence=0.0,
            trigger_price=None,
            previous_level=None,
            pullback_low=None,
            pullback_high=None,
            reason="Lifecycle direction is neutral.",
        )

    def _analyze_long(
        self,
        *,
        symbol: str,
        previous_bar,
        current_bar,
        atr14: float | None,
    ) -> AcceptanceResult:
        previous_level = previous_bar.high

        if current_bar.close <= previous_level:
            return AcceptanceResult(
                symbol=symbol,
                accepted=False,
                direction="long",
                level=ACCEPTANCE_NONE,
                score=0,
                confidence=0.0,
                trigger_price=None,
                previous_level=previous_level,
                pullback_low=previous_bar.low,
                pullback_high=previous_bar.high,
                reason=(
                    "Current completed candle did not close above "
                    "the prior candle high."
                ),
            )

        score, evidence, warnings = self._score_candle(
            current_bar=current_bar,
            atr14=atr14,
            bullish=True,
        )

        score += 50

        evidence.insert(
            0,
            "Current candle closed above the prior candle high.",
        )

        level = self._map_level(score)

        return AcceptanceResult(
            symbol=symbol,
            accepted=True,
            direction="long",
            level=level,
            score=score,
            confidence=float(score),
            trigger_price=current_bar.close,
            previous_level=previous_level,
            pullback_low=previous_bar.low,
            pullback_high=previous_bar.high,
            evidence=evidence,
            warnings=warnings,
            reason="Bullish candle-close acceptance confirmed.",
        )

    def _analyze_short(
        self,
        *,
        symbol: str,
        previous_bar,
        current_bar,
        atr14: float | None,
    ) -> AcceptanceResult:
        previous_level = previous_bar.low

        if current_bar.close >= previous_level:
            return AcceptanceResult(
                symbol=symbol,
                accepted=False,
                direction="short",
                level=ACCEPTANCE_NONE,
                score=0,
                confidence=0.0,
                trigger_price=None,
                previous_level=previous_level,
                pullback_low=previous_bar.low,
                pullback_high=previous_bar.high,
                reason=(
                    "Current completed candle did not close below "
                    "the prior candle low."
                ),
            )

        score, evidence, warnings = self._score_candle(
            current_bar=current_bar,
            atr14=atr14,
            bullish=False,
        )

        score += 50

        evidence.insert(
            0,
            "Current candle closed below the prior candle low.",
        )

        level = self._map_level(score)

        return AcceptanceResult(
            symbol=symbol,
            accepted=True,
            direction="short",
            level=level,
            score=score,
            confidence=float(score),
            trigger_price=current_bar.close,
            previous_level=previous_level,
            pullback_low=previous_bar.low,
            pullback_high=previous_bar.high,
            evidence=evidence,
            warnings=warnings,
            reason="Bearish candle-close acceptance confirmed.",
        )

    def _score_candle(
        self,
        *,
        current_bar,
        atr14: float | None,
        bullish: bool,
    ) -> tuple[int, list[str], list[str]]:
        score = 0
        evidence: list[str] = []
        warnings: list[str] = []

        candle_range = current_bar.high - current_bar.low
        body_size = abs(
            current_bar.close - current_bar.open
        )

        if candle_range <= 0:
            return (
                score,
                evidence,
                [
                    "Acceptance candle has no measurable range."
                ],
            )

        body_ratio = body_size / candle_range

        if body_ratio >= 0.60:
            score += 20
            evidence.append(
                "Candle body is at least 60% of its range."
            )
        else:
            warnings.append(
                "Acceptance candle body is less than 60% "
                "of its range."
            )

        if bullish:
            close_location = (
                current_bar.close - current_bar.low
            ) / candle_range

            if close_location >= 0.75:
                score += 20
                evidence.append(
                    "Candle closed in the upper 25% of its range."
                )
            else:
                warnings.append(
                    "Candle did not close near its high."
                )
        else:
            close_location = (
                current_bar.high - current_bar.close
            ) / candle_range

            if close_location >= 0.75:
                score += 20
                evidence.append(
                    "Candle closed in the lower 25% of its range."
                )
            else:
                warnings.append(
                    "Candle did not close near its low."
                )

        if atr14 is not None and atr14 > 0:
            if candle_range >= atr14 * 0.80:
                score += 10
                evidence.append(
                    "Candle range is at least 0.8 ATR."
                )
            else:
                warnings.append(
                    "Acceptance candle range is below 0.8 ATR."
                )
        else:
            warnings.append(
                "ATR14 was unavailable for range scoring."
            )

        return score, evidence, warnings

    def _map_level(self, score: int) -> str:
        if score >= 90:
            return ACCEPTANCE_EXCEPTIONAL

        if score >= 70:
            return ACCEPTANCE_STRONG

        if score >= 50:
            return ACCEPTANCE_GOOD

        return ACCEPTANCE_NONE