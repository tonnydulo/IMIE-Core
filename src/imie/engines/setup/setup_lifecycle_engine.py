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
    analyst_name = "SetupLifecycleAnalyst"

    def analyze(
        self,
        context: TradingContext,
        trend_result: AnalystResult,
        acceptance_confirmed: bool = False,
    ) -> AnalystResult:
        """
        Return the standardized analyst result.

        The detailed SetupLifecycle object is retained in payload.
        """

        lifecycle = self.evaluate_pullback_to_core(
            context=context,
            trend_result=trend_result,
            acceptance_confirmed=acceptance_confirmed,
        )

        evidence = [
            f"Setup lifecycle is {lifecycle.state}.",
            lifecycle.reason,
        ]

        warnings: list[str] = []

        if lifecycle.state == LIFECYCLE_DISCOVERY:
            warnings.append("The setup has not developed into a tradable state.")

        elif lifecycle.state == LIFECYCLE_EXTENDED:
            warnings.append("Price is extended from Core. Do not chase the move.")

        elif lifecycle.state == LIFECYCLE_TRENDING:
            warnings.append("Price is not yet close enough to Core.")

        elif lifecycle.state == LIFECYCLE_RETURNING_TO_CORE:
            warnings.append("Acceptance cannot be evaluated until price reaches Core.")

        elif lifecycle.state == LIFECYCLE_AT_CORE:
            warnings.append("Completed-candle acceptance is still required.")

        return AnalystResult(
            analyst=self.analyst_name,
            opinion=lifecycle.state,
            confidence=float(lifecycle.confidence),
            evidence=evidence,
            warnings=warnings,
            payload=lifecycle,
        )

    def evaluate_pullback_to_core(
        self,
        context: TradingContext,
        trend_result: AnalystResult,
        acceptance_confirmed: bool = False,
    ) -> SetupLifecycle:
        """
        Build the detailed Pullback-to-Core lifecycle result.

        This method remains available so existing code continues to work.
        """

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

        direction = (
            "long"
            if trend_result.opinion == TREND_BULLISH
            else "short"
        )

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

        if (
            acceptance_confirmed
            and context.observations.within_core_zone
        ):
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
                reason=(
                    "Price is inside the Core zone. "
                    "Watch for prior candle reclaim."
                ),
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