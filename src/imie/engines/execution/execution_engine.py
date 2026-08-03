from imie.engines.execution.execution_models import ExecutionState
from imie.models import MarketSnapshot


class ExecutionEngine:
    def __init__(self, atr_tolerance: float = 0.25) -> None:
        self.atr_tolerance = atr_tolerance

    def analyze_pullback_to_core(self, snapshot: MarketSnapshot) -> ExecutionState:
        facts = snapshot.facts
        quote = snapshot.quote

        if facts.ema9 is None or facts.vwap is None or facts.atr14 is None:
            return ExecutionState(
                symbol=snapshot.symbol,
                direction="neutral",
                state="IDLE",
                core_type="none",
                core_price=None,
                distance_to_core=None,
                atr=facts.atr14,
                tolerance=None,
                reason="Missing EMA9, VWAP, or ATR14.",
            )

        last_price = quote.last
        tolerance = facts.atr14 * self.atr_tolerance

        direction = self._detect_direction(last_price, facts.ema9, facts.vwap)

        if direction == "neutral":
            return ExecutionState(
                symbol=snapshot.symbol,
                direction=direction,
                state="IDLE",
                core_type="none",
                core_price=None,
                distance_to_core=None,
                atr=facts.atr14,
                tolerance=tolerance,
                reason="Price is not clearly aligned above or below EMA9 and VWAP.",
            )

        ema_distance = abs(last_price - facts.ema9)
        vwap_distance = abs(last_price - facts.vwap)

        if ema_distance <= vwap_distance:
            core_type = "EMA9"
            core_price = facts.ema9
            distance = ema_distance
        else:
            core_type = "VWAP"
            core_price = facts.vwap
            distance = vwap_distance

        if distance <= tolerance:
            state = "AT_CORE"
            reason = f"Price is within 0.25 ATR of {core_type}."
        else:
            state = "DEVELOPING"
            reason = f"Price is trending but not yet inside the core zone. Nearest core is {core_type}."

        return ExecutionState(
            symbol=snapshot.symbol,
            direction=direction,
            state=state,
            core_type=core_type,
            core_price=core_price,
            distance_to_core=distance,
            atr=facts.atr14,
            tolerance=tolerance,
            reason=reason,
        )

    def _detect_direction(self, price: float, ema9: float, vwap: float) -> str:
        if price > ema9 and price > vwap:
            return "long"

        if price < ema9 and price < vwap:
            return "short"

        return "neutral"
