from imie.models import AnalystResult, TradingContext
from imie.utils.constants import TREND_BEARISH, TREND_BULLISH, TREND_NEUTRAL


class TrendAnalyst:
    analyst_name = "TrendAnalyst"

    def analyze(self, context: TradingContext) -> AnalystResult:
        observations = context.observations

        bullish_score = 0
        bearish_score = 0
        evidence: list[str] = []
        warnings: list[str] = []

        if observations.price_above_ema9:
            bullish_score += 40
            evidence.append("Price is above EMA9.")
        elif observations.price_below_ema9:
            bearish_score += 40
            evidence.append("Price is below EMA9.")
        else:
            warnings.append("Price is not clearly separated from EMA9.")

        if observations.price_above_vwap:
            bullish_score += 30
            evidence.append("Price is above VWAP.")
        elif observations.price_below_vwap:
            bearish_score += 30
            evidence.append("Price is below VWAP.")
        else:
            warnings.append("Price is not clearly separated from VWAP.")

        if observations.ema9_rising:
            bullish_score += 30
            evidence.append("EMA9 is rising.")
        elif observations.ema9_falling:
            bearish_score += 30
            evidence.append("EMA9 is falling.")
        else:
            warnings.append("EMA9 slope is flat or unavailable.")

        if bullish_score > bearish_score and bullish_score >= 60:
            return AnalystResult(
                analyst=self.analyst_name,
                opinion=TREND_BULLISH,
                confidence=float(bullish_score),
                evidence=evidence,
                warnings=warnings,
            )

        if bearish_score > bullish_score and bearish_score >= 60:
            return AnalystResult(
                analyst=self.analyst_name,
                opinion=TREND_BEARISH,
                confidence=float(bearish_score),
                evidence=evidence,
                warnings=warnings,
            )

        return AnalystResult(
            analyst=self.analyst_name,
            opinion=TREND_NEUTRAL,
            confidence=float(max(bullish_score, bearish_score)),
            evidence=evidence,
            warnings=warnings + ["Trend is mixed or not strong enough."],
        )
