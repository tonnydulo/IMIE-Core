from imie.indicators import calculate_atr_wilder, calculate_ema, calculate_vwap
from imie.models import MarketBar, MarketFacts, MarketSnapshot


class FactsEngine:
    def build_facts(self, bars: list[MarketBar]) -> MarketFacts:
        return MarketFacts(
            ema9=calculate_ema(
                bars,
                period=9,
                seed_method="first",
            ),
            vwap=calculate_vwap(
                bars,
                include_extended_hours=False,
            ),
            atr14=calculate_atr_wilder(
                bars,
                period=14,
            ),
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

    def calculate_ema(
        self,
        bars: list[MarketBar],
        period: int,
    ) -> float | None:
        return calculate_ema(
            bars,
            period,
            seed_method="first",
        )

    def calculate_vwap(
        self,
        bars: list[MarketBar],
        *,
        include_extended_hours: bool = False,
    ) -> float | None:
        return calculate_vwap(
            bars,
            include_extended_hours=include_extended_hours,
        )

    def calculate_atr(
        self,
        bars: list[MarketBar],
        period: int = 14,
    ) -> float | None:
        return calculate_atr_wilder(bars, period)
