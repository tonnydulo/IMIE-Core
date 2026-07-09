from imie.engines.facts import FactsEngine
from imie.models import MarketBar, MarketMeasurements, MarketObservations, MarketSnapshot, TradingContext


class ContextBuilder:
    def __init__(self, atr_tolerance: float = 0.25, approaching_atr_distance: float = 2.0) -> None:
        self.facts_engine = FactsEngine()
        self.atr_tolerance = atr_tolerance
        self.approaching_atr_distance = approaching_atr_distance

    def build(self, snapshot: MarketSnapshot) -> TradingContext:
        enriched_snapshot = self.facts_engine.enrich_snapshot(snapshot)
        measurements = self._build_measurements(enriched_snapshot)
        observations = self._build_observations(measurements)

        return TradingContext(
            snapshot=enriched_snapshot,
            measurements=measurements,
            observations=observations,
        )

    def _build_measurements(self, snapshot: MarketSnapshot) -> MarketMeasurements:
        price = snapshot.quote.last
        ema9 = snapshot.facts.ema9
        previous_ema9 = self._calculate_previous_ema(snapshot.bars, period=9)
        ema9_slope = None

        if ema9 is not None and previous_ema9 is not None:
            ema9_slope = ema9 - previous_ema9

        nearest_core = "none"
        nearest_core_price = None
        distance_to_core = None
        atr_distance_to_core = None
        core_tolerance = None

        if ema9 is not None and snapshot.facts.vwap is not None and snapshot.facts.atr14 is not None:
            ema_distance = abs(price - ema9)
            vwap_distance = abs(price - snapshot.facts.vwap)

            if ema_distance <= vwap_distance:
                nearest_core = "EMA9"
                nearest_core_price = ema9
                distance_to_core = ema_distance
            else:
                nearest_core = "VWAP"
                nearest_core_price = snapshot.facts.vwap
                distance_to_core = vwap_distance

            core_tolerance = snapshot.facts.atr14 * self.atr_tolerance

            if snapshot.facts.atr14 > 0:
                atr_distance_to_core = distance_to_core / snapshot.facts.atr14

        return MarketMeasurements(
            price=price,
            ema9=ema9,
            previous_ema9=previous_ema9,
            ema9_slope=ema9_slope,
            vwap=snapshot.facts.vwap,
            atr14=snapshot.facts.atr14,
            nearest_core=nearest_core,
            nearest_core_price=nearest_core_price,
            distance_to_core=distance_to_core,
            atr_distance_to_core=atr_distance_to_core,
            core_tolerance=core_tolerance,
        )

    def _build_observations(self, measurements: MarketMeasurements) -> MarketObservations:
        price_above_ema9 = measurements.ema9 is not None and measurements.price > measurements.ema9
        price_below_ema9 = measurements.ema9 is not None and measurements.price < measurements.ema9
        price_above_vwap = measurements.vwap is not None and measurements.price > measurements.vwap
        price_below_vwap = measurements.vwap is not None and measurements.price < measurements.vwap
        ema9_rising = measurements.ema9_slope is not None and measurements.ema9_slope > 0
        ema9_falling = measurements.ema9_slope is not None and measurements.ema9_slope < 0
        within_core_zone = (
            measurements.distance_to_core is not None
            and measurements.core_tolerance is not None
            and measurements.distance_to_core <= measurements.core_tolerance
        )
        approaching_core = (
            measurements.atr_distance_to_core is not None
            and measurements.atr_distance_to_core <= self.approaching_atr_distance
            and not within_core_zone
        )

        return MarketObservations(
            price_above_ema9=price_above_ema9,
            price_below_ema9=price_below_ema9,
            price_above_vwap=price_above_vwap,
            price_below_vwap=price_below_vwap,
            ema9_rising=ema9_rising,
            ema9_falling=ema9_falling,
            within_core_zone=within_core_zone,
            approaching_core=approaching_core,
        )

    def _calculate_previous_ema(self, bars: list[MarketBar], period: int) -> float | None:
        if len(bars) < period + 2:
            return None

        return self.facts_engine.calculate_ema(bars[:-1], period=period)
