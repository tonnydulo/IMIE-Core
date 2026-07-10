from imie.models import (
    AcceptanceResult,
    AnalystResult,
    DataFreshness,
    SetupLifecycle,
    TradePlan,
    TradingContext,
)
from imie.utils.constants import (
    DECISION_PASS,
    DECISION_READY,
    DECISION_WAIT,
    LIFECYCLE_READY,
    STRATEGY_PULLBACK_TO_CORE,
)


class RiskAnalyst:
    analyst_name = "RiskAnalyst"

    def __init__(
        self,
        *,
        minimum_rr: float = 2.0,
        target1_r: float = 1.0,
        target2_r: float = 2.0,
    ) -> None:
        if minimum_rr <= 0:
            raise ValueError("Minimum RR must be greater than zero.")

        if target1_r <= 0 or target2_r <= 0:
            raise ValueError("Target multiples must be greater than zero.")

        if target2_r < target1_r:
            raise ValueError("Target 2 must not be smaller than Target 1.")

        self.minimum_rr = minimum_rr
        self.target1_r = target1_r
        self.target2_r = target2_r

    def analyze(
        self,
        *,
        context: TradingContext,
        freshness: DataFreshness,
        trend_result: AnalystResult,
        lifecycle: SetupLifecycle,
        acceptance: AcceptanceResult,
    ) -> TradePlan:
        reasons: list[str] = []
        warnings: list[str] = []

        if not freshness.actionable:
            warnings.append(freshness.reason)

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_PASS,
                warnings=warnings,
                narrative=(
                    "No trade plan was authorized because the market data "
                    "was stale or misaligned."
                ),
            )

        if not acceptance.accepted:
            warnings.append("Candle-close acceptance has not been confirmed.")

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_WAIT,
                warnings=warnings,
                narrative=(
                    "The trend and setup may still be developing, but the "
                    "required candle-close acceptance trigger is missing."
                ),
            )

        if lifecycle.state != LIFECYCLE_READY:
            warnings.append("Setup lifecycle has not advanced to READY.")

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_WAIT,
                warnings=warnings,
                narrative="The setup is not yet ready for risk evaluation.",
            )

        entry = acceptance.trigger_price

        if entry is None:
            warnings.append("Acceptance trigger price is unavailable.")

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_PASS,
                warnings=warnings,
                narrative="A valid entry price could not be determined.",
            )

        if lifecycle.direction == "long":
            stop = acceptance.pullback_low

            if stop is None or stop >= entry:
                warnings.append("Long stop must be below the entry price.")

                return self._empty_plan(
                    symbol=context.snapshot.symbol,
                    direction=lifecycle.direction,
                    decision=DECISION_PASS,
                    warnings=warnings,
                    narrative="The proposed long stop is structurally invalid.",
                )

            risk_per_share = entry - stop
            target1 = entry + risk_per_share * self.target1_r
            target2 = entry + risk_per_share * self.target2_r

        elif lifecycle.direction == "short":
            stop = acceptance.pullback_high

            if stop is None or stop <= entry:
                warnings.append("Short stop must be above the entry price.")

                return self._empty_plan(
                    symbol=context.snapshot.symbol,
                    direction=lifecycle.direction,
                    decision=DECISION_PASS,
                    warnings=warnings,
                    narrative="The proposed short stop is structurally invalid.",
                )

            risk_per_share = stop - entry
            target1 = entry - risk_per_share * self.target1_r
            target2 = entry - risk_per_share * self.target2_r

        else:
            warnings.append("Trade direction is neutral.")

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_PASS,
                warnings=warnings,
                narrative="No directional trade plan can be created.",
            )

        if risk_per_share <= 0:
            warnings.append("Risk per share must be greater than zero.")

            return self._empty_plan(
                symbol=context.snapshot.symbol,
                direction=lifecycle.direction,
                decision=DECISION_PASS,
                warnings=warnings,
                narrative="The calculated risk is invalid.",
            )

        reward1 = risk_per_share * self.target1_r
        reward2 = risk_per_share * self.target2_r
        rr1 = reward1 / risk_per_share
        rr2 = reward2 / risk_per_share

        reasons.extend(
            [
                f"Data freshness status is {freshness.status}.",
                f"Trend opinion is {trend_result.opinion}.",
                f"Acceptance level is {acceptance.level}.",
                "Entry uses the completed acceptance candle close.",
                "Stop uses the pullback candle invalidation level.",
                f"Projected Target 2 provides {rr2:.2f}R.",
            ]
        )

        quality = self._calculate_quality(
            trend_confidence=trend_result.confidence,
            acceptance_score=acceptance.score,
            rr2=rr2,
        )

        confidence = (
            trend_result.confidence * 0.40
            + acceptance.confidence * 0.40
            + min(rr2 / self.minimum_rr, 1.0) * 100.0 * 0.20
        )

        valid = rr2 >= self.minimum_rr
        actionable = valid and freshness.actionable

        if not valid:
            warnings.append(
                f"Projected RR {rr2:.2f} is below the "
                f"{self.minimum_rr:.2f} minimum."
            )

        decision = DECISION_READY if actionable else DECISION_PASS

        narrative = self._build_narrative(
            direction=lifecycle.direction,
            trend_opinion=trend_result.opinion,
            acceptance_level=acceptance.level,
            entry=entry,
            stop=stop,
            target2=target2,
            rr2=rr2,
            actionable=actionable,
        )

        return TradePlan(
            symbol=context.snapshot.symbol,
            strategy=STRATEGY_PULLBACK_TO_CORE,
            direction=lifecycle.direction,
            valid=valid,
            actionable=actionable,
            decision=decision,
            entry=entry,
            stop=stop,
            target1=target1,
            target2=target2,
            risk_per_share=risk_per_share,
            reward1_per_share=reward1,
            reward2_per_share=reward2,
            rr1=rr1,
            rr2=rr2,
            quality=quality,
            confidence=min(100.0, confidence),
            reasons=reasons,
            warnings=warnings,
            narrative=narrative,
        )

    def _calculate_quality(
        self,
        *,
        trend_confidence: float,
        acceptance_score: int,
        rr2: float,
    ) -> int:
        trend_component = trend_confidence * 0.40
        acceptance_component = acceptance_score * 0.40
        risk_component = min(rr2 / self.minimum_rr, 1.0) * 20.0

        return round(
            min(
                100.0,
                trend_component
                + acceptance_component
                + risk_component,
            )
        )

    def _build_narrative(
        self,
        *,
        direction: str,
        trend_opinion: str,
        acceptance_level: str,
        entry: float,
        stop: float,
        target2: float,
        rr2: float,
        actionable: bool,
    ) -> str:
        status = "actionable" if actionable else "not actionable"

        return (
            f"A {direction} Pullback-to-Core setup is {status}. "
            f"The trend analyst reported {trend_opinion}, and "
            f"candle-close acceptance was rated {acceptance_level}. "
            f"The projected entry is {entry:.2f}, invalidation is "
            f"{stop:.2f}, and the 2R target is {target2:.2f}. "
            f"Projected reward-to-risk is {rr2:.2f}."
        )

    def _empty_plan(
        self,
        *,
        symbol: str,
        direction: str,
        decision: str,
        warnings: list[str],
        narrative: str,
    ) -> TradePlan:
        return TradePlan(
            symbol=symbol,
            strategy=STRATEGY_PULLBACK_TO_CORE,
            direction=direction,
            valid=False,
            actionable=False,
            decision=decision,
            entry=None,
            stop=None,
            target1=None,
            target2=None,
            risk_per_share=None,
            reward1_per_share=None,
            reward2_per_share=None,
            rr1=None,
            rr2=None,
            quality=0,
            confidence=0.0,
            reasons=[],
            warnings=warnings,
            narrative=narrative,
        )
