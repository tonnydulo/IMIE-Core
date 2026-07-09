from imie.models import AnalystResult, SetupLifecycle, TradingContext
from imie.utils.constants import (
    ACTION_BUILD_WATCHLIST,
    ACTION_EVALUATE_ENTRY,
    ACTION_IGNORE,
    ACTION_MONITOR,
    ACTION_PREPARE,
    ACTION_WAIT,
    LIFECYCLE_AT_CORE,
    LIFECYCLE_DISCOVERY,
    LIFECYCLE_EXTENDED,
    LIFECYCLE_READY,
    LIFECYCLE_RETURNING_TO_CORE,
    LIFECYCLE_TRENDING,
    TREND_BEARISH,
    TREND_BULLISH,
)


class SetupLifecycleEngine:
    def evaluate_pullback_to_core(
        self,
        context: TradingContext,
        trend_result: AnalystResult,
        acceptance_confirmed: bool = False,
    ) -> SetupLifecycle:
        symbol = context.snapshot.symbol
        atr_distance = context.measurements.atr_distance_to_core

        if trend_result.opinion not in [TREND_BULLISH, TREND_BEARISH]:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_DISCOVERY,
                direction="neutral",
                confidence=0,
                atr_distance=atr_distance,
                action=ACTION_BUILD_WATCHLIST,
                reason="No tradable trend confirmed yet.",
            )

        direction = "long" if trend_result.opinion == TREND_BULLISH else "short"

        if atr_distance is None:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_DISCOVERY,
                direction=direction,
                confidence=trend_result.confidence,
                atr_distance=None,
                action=ACTION_BUILD_WATCHLIST,
                reason="ATR distance to Core is unavailable.",
            )

        if acceptance_confirmed and context.observations.within_core_zone:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_READY,
                direction=direction,
                confidence=min(100, trend_result.confidence),
                atr_distance=atr_distance,
                action=ACTION_EVALUATE_ENTRY,
                reason="Acceptance confirmed at Core.",
            )

        if context.observations.within_core_zone:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_AT_CORE,
                direction=direction,
                confidence=min(95, trend_result.confidence),
                atr_distance=atr_distance,
                action=ACTION_PREPARE,
                reason="Price is inside the Core zone. Watch for prior candle reclaim.",
            )

        if atr_distance <= 2:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_RETURNING_TO_CORE,
                direction=direction,
                confidence=min(90, trend_result.confidence),
                atr_distance=atr_distance,
                action=ACTION_MONITOR,
                reason="Price is returning toward Core.",
            )

        if atr_distance > 10:
            return SetupLifecycle(
                symbol=symbol,
                state=LIFECYCLE_EXTENDED,
                direction=direction,
                confidence=min(85, trend_result.confidence),
                atr_distance=atr_distance,
                action=ACTION_WAIT,
                reason="Price is significantly extended from Core.",
            )

        return SetupLifecycle(
            symbol=symbol,
            state=LIFECYCLE_TRENDING,
            direction=direction,
            confidence=min(80, trend_result.confidence),
            atr_distance=atr_distance,
            action=ACTION_IGNORE,
            reason="Trend exists, but price is not close enough to Core.",
        )
