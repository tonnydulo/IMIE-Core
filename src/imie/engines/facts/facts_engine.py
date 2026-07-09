from imie.indicators import calculate_atr_wilder, calculate_ema, calculate_vwap
from imie.models import MarketBar, MarketFacts, MarketSnapshot


class FactsEngine:
    def build_facts(self, bars: list[MarketBar]) -> MarketFacts:
        return MarketFacts(
            ema9=calculate_ema(bars, period=9),
            vwap=calculate_vwap(bars),
            atr14=calculate_atr_wilder(bars, period=14),
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
        return calculate_ema(bars, period)

    def calculate_vwap(self, bars: list[MarketBar]) -> float | None:
        return calculate_vwap(bars)

    def calculate_atr(self, bars: list[MarketBar], period: int = 14) -> float | None:
        return calculate_atr_wilder(bars, period)
