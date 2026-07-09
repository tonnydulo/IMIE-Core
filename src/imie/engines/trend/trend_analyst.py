from imie.models import AnalystResult, MarketSnapshot
from imie.utils.constants import TREND_BEARISH, TREND_BULLISH, TREND_NEUTRAL


class TrendAnalyst:
    analyst_name = "TrendAnalyst"

    def analyze(self, snapshot: MarketSnapshot) -> AnalystResult:
        facts = snapshot.facts
        price = snapshot.quote.last

        if facts.ema9 is None or facts.vwap is None:
            return AnalystResult(
                analyst=self.analyst_name,
                opinion=TREND_NEUTRAL,
                confidence=0,
                warnings=["Missing EMA9 or VWAP."],
            )

        bullish_score = 0
        bearish_score = 0
        evidence: list[str] = []
        warnings: list[str] = []

        if price > facts.ema9:
            bullish_score += 40
            evidence.append("Price is above EMA9.")
        elif price < facts.ema9:
            bearish_score += 40
            evidence.append("Price is below EMA9.")
        else:
            warnings.append("Price is exactly at EMA9.")

        if price > facts.vwap:
            bullish_score += 30
            evidence.append("Price is above VWAP.")
        elif price < facts.vwap:
            bearish_score += 30
            evidence.append("Price is below VWAP.")
        else:
            warnings.append("Price is exactly at VWAP.")

        ema_slope = self._calculate_ema9_slope(snapshot)

        if ema_slope is None:
            warnings.append("EMA9 slope unavailable.")
        elif ema_slope > 0:
            bullish_score += 30
            evidence.append("EMA9 is rising.")
        elif ema_slope < 0:
            bearish_score += 30
            evidence.append("EMA9 is falling.")
        else:
            warnings.append("EMA9 is flat.")

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

    def _calculate_ema9_slope(self, snapshot: MarketSnapshot) -> float | None:
        bars = snapshot.bars

        if len(bars) < 20:
            return None

        recent_close = bars[-1].close
        previous_close = bars[-5].close

        return recent_close - previous_close
