from imie.models import MarketBar, MarketFacts, MarketSnapshot


class FactsEngine:
    def build_facts(self, bars: list[MarketBar]) -> MarketFacts:
        return MarketFacts(
            ema9=self.calculate_ema(bars, period=9),
            vwap=self.calculate_vwap(bars),
            atr14=self.calculate_atr(bars, period=14),
        )

    def enrich_snapshot(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        facts = self.build_facts(snapshot.bars)

        return MarketSnapshot(
            symbol=snapshot.symbol,
            timestamp=snapshot.timestamp,
            quote=snapshot.quote,
            bars=snapshot.bars,
            timeframe=snapshot.timeframe,
            facts=facts,
        )

    def calculate_ema(self, bars: list[MarketBar], period: int) -> float | None:
        if len(bars) < period:
            return None

        closes = [bar.close for bar in bars]
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period

        for close in closes[period:]:
            ema = (close - ema) * multiplier + ema

        return ema

    def calculate_vwap(self, bars: list[MarketBar]) -> float | None:
        total_price_volume = 0.0
        total_volume = 0

        for bar in bars:
            typical_price = (bar.high + bar.low + bar.close) / 3
            total_price_volume += typical_price * bar.volume
            total_volume += bar.volume

        if total_volume == 0:
            return None

        return total_price_volume / total_volume

    def calculate_atr(self, bars: list[MarketBar], period: int = 14) -> float | None:
        if len(bars) < period + 1:
            return None

        true_ranges: list[float] = []

        for i in range(1, len(bars)):
            current = bars[i]
            previous = bars[i - 1]

            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )

            true_ranges.append(tr)

        recent_ranges = true_ranges[-period:]
        return sum(recent_ranges) / period
