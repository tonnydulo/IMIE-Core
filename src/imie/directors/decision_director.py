from __future__ import annotations

from dataclasses import dataclass

from imie.directors.institutional_confluence_engine import (
    InstitutionalConfluenceEngine,
)
from imie.models import (
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    DecisionResult,
    DirectorDecision,
    InstitutionalConfluence,
    InstitutionalDirection,
    TradePlan,
    TradingContext,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_LIQUIDITY,
    ANALYST_ORDER_BLOCK,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_STRUCTURE,
    ANALYST_TREND,
    CORE_ANALYST_IDS,
)
from imie.utils.constants import (
    LIFECYCLE_AT_CORE,
    LIFECYCLE_DISCOVERY,
    LIFECYCLE_EXTENDED,
    LIFECYCLE_READY,
    LIFECYCLE_RETURNING_TO_CORE,
    LIFECYCLE_TRENDING,
    TREND_BEARISH,
    TREND_BULLISH,
    TREND_NEUTRAL,
)


@dataclass(frozen=True, slots=True)
class DecisionDirectorConfig:
    """
    Configuration for final trade authorization.
    """

    minimum_ready_confidence: float = 60.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_ready_confidence <= 100.0:
            raise ValueError(
                "minimum_ready_confidence must be between 0 and 100."
            )


class DecisionDirector:
    """
    Produces the final explainable IMIE recommendation.

    Required authorization analysts:

    - Trend
    - Setup
    - Acceptance
    - Risk

    Optional institutional context:

    - Structure
    - Liquidity
    - Order Blocks

    Institutional confluence may enrich evidence, add warnings,
    and apply a bounded confidence bonus.

    The confluence bonus is applied only when the dominant
    institutional direction aligns with the intended trade
    direction.

    Confluence never overrides Trend, Setup, Acceptance, Risk,
    or an invalid TradePlan.
    """

    def __init__(
        self,
        config: DecisionDirectorConfig | None = None,
        confluence_engine: (
            InstitutionalConfluenceEngine | None
        ) = None,
    ) -> None:
        self.config = (
            config
            or DecisionDirectorConfig()
        )

        self.confluence_engine = (
            confluence_engine
            or InstitutionalConfluenceEngine()
        )

        if not isinstance(
            self.confluence_engine,
            InstitutionalConfluenceEngine,
        ):
            raise TypeError(
                "confluence_engine must be an "
                "InstitutionalConfluenceEngine."
            )

    def evaluate(
        self,
        *,
        context: TradingContext,
        freshness: DataFreshness,
        registry: AnalystRegistry,
    ) -> DecisionResult:
        """
        Produce the final system-level recommendation.
        """

        del context

        if not freshness.actionable:
            return DecisionResult(
                decision=DirectorDecision.PASS,
                actionable=False,
                confidence=0.0,
                recommendation=(
                    "Do not evaluate trading opportunities until "
                    "fresh, aligned market data is available."
                ),
                reasons=(
                    freshness.reason,
                ),
                warnings=(
                    "Decision Director halted because market data "
                    "failed freshness validation.",
                ),
                analyst_summary={},
                trade_plan=None,
            )

        summary = self._build_summary(
            registry
        )

        reasons = self._collect_evidence(
            registry
        )

        warnings = self._collect_warnings(
            registry
        )

        missing = self._missing_required_analysts(
            registry
        )

        if missing:
            missing_text = ", ".join(
                missing
            )

            return DecisionResult(
                decision=DirectorDecision.WAIT,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Wait until all required analysts have reported."
                ),
                reasons=(
                    (
                        "Required analyst results are missing: "
                        f"{missing_text}."
                    ),
                ),
                warnings=warnings,
                analyst_summary=summary,
            )

        disabled = self._disabled_required_analysts(
            registry
        )

        if disabled:
            disabled_text = ", ".join(
                disabled
            )

            return DecisionResult(
                decision=DirectorDecision.WAIT,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Wait until all required analysts are enabled."
                ),
                reasons=(
                    (
                        "Required analysts are disabled: "
                        f"{disabled_text}."
                    ),
                ),
                warnings=warnings,
                analyst_summary=summary,
            )

        trend_result = self._require(
            registry,
            ANALYST_TREND,
        )

        setup_result = self._require(
            registry,
            ANALYST_SETUP,
        )

        acceptance_result = self._require(
            registry,
            ANALYST_ACCEPTANCE,
        )

        risk_result = self._require(
            registry,
            ANALYST_RISK,
        )

        structure_result = registry.get(
            ANALYST_STRUCTURE
        )

        liquidity_result = registry.get(
            ANALYST_LIQUIDITY
        )

        order_block_result = registry.get(
            ANALYST_ORDER_BLOCK
        )

        order_block_evidence, order_block_warnings = (
            self._order_block_support(
                order_block_result
            )
        )

        liquidity_evidence, liquidity_warnings = (
            self._liquidity_support(
                liquidity_result
            )
        )

        confluence = self.confluence_engine.evaluate(
            structure=structure_result,
            liquidity=liquidity_result,
            order_block=order_block_result,
        )

        reasons = self._merge_items(
            (
                *reasons,
                *order_block_evidence,
                *liquidity_evidence,
                *confluence.evidence,
            )
        )

        warnings = self._merge_items(
            (
                *warnings,
                *order_block_warnings,
                *liquidity_warnings,
                *confluence.warnings,
            )
        )

        trend_opinion = self._normalize(
            trend_result.opinion
        )

        setup_opinion = self._normalize(
            setup_result.opinion
        )

        trade_direction = self._trend_direction(
            trend_result
        )

        directional_reasons, directional_warnings = (
            self._directional_confluence_context(
                confluence=confluence,
                trade_direction=trade_direction,
            )
        )

        reasons = self._merge_items(
            (
                *reasons,
                *directional_reasons,
            )
        )

        warnings = self._merge_items(
            (
                *warnings,
                *directional_warnings,
            )
        )

        if trend_opinion == self._normalize(
            TREND_NEUTRAL
        ):
            return DecisionResult(
                decision=DirectorDecision.IGNORE,
                actionable=False,
                confidence=trend_result.confidence,
                recommendation=(
                    "Ignore the setup until directional trend "
                    "alignment is established."
                ),
                reasons=self._merge_items(
                    (
                        "Trend analysis is neutral.",
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        valid_trends = {
            self._normalize(
                TREND_BULLISH
            ),
            self._normalize(
                TREND_BEARISH
            ),
        }

        if trend_opinion not in valid_trends:
            return DecisionResult(
                decision=DirectorDecision.IGNORE,
                actionable=False,
                confidence=trend_result.confidence,
                recommendation=(
                    "Ignore the setup because the trend opinion "
                    "is not tradable."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Trend opinion is "
                            f"{trend_result.opinion}."
                        ),
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        waiting_states = {
            self._normalize(
                LIFECYCLE_DISCOVERY
            ),
            self._normalize(
                LIFECYCLE_TRENDING
            ),
            self._normalize(
                LIFECYCLE_EXTENDED
            ),
        }

        if setup_opinion in waiting_states:
            return DecisionResult(
                decision=DirectorDecision.WAIT,
                actionable=False,
                confidence=self._average_confidence(
                    trend_result,
                    setup_result,
                ),
                recommendation=self._wait_recommendation(
                    setup_opinion
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Setup lifecycle is "
                            f"{setup_result.opinion}."
                        ),
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        if setup_opinion == self._normalize(
            LIFECYCLE_RETURNING_TO_CORE
        ):
            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=self._average_confidence(
                    trend_result,
                    setup_result,
                ),
                recommendation=(
                    "Prepare for a possible Pullback-to-Core setup. "
                    "Wait for price to reach Core and confirm "
                    "acceptance."
                ),
                reasons=self._merge_items(
                    (
                        "Price is returning toward Core.",
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        acceptance_confirmed = (
            self._acceptance_confirmed(
                acceptance_result
            )
        )

        if (
            setup_opinion
            == self._normalize(
                LIFECYCLE_AT_CORE
            )
            and not acceptance_confirmed
        ):
            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=self._average_confidence(
                    trend_result,
                    setup_result,
                ),
                recommendation=(
                    "Price is at Core. Wait for completed-candle "
                    "acceptance before considering execution."
                ),
                reasons=self._merge_items(
                    (
                        "Price has reached Core.",
                        "Acceptance has not been confirmed.",
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        if setup_opinion not in {
            self._normalize(
                LIFECYCLE_AT_CORE
            ),
            self._normalize(
                LIFECYCLE_READY
            ),
        }:
            return DecisionResult(
                decision=DirectorDecision.WAIT,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Wait for the setup lifecycle to progress."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Setup lifecycle is "
                            f"{setup_result.opinion}."
                        ),
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        if not acceptance_confirmed:
            return DecisionResult(
                decision=DirectorDecision.WAIT,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Wait for completed-candle acceptance "
                    "confirmation."
                ),
                reasons=self._merge_items(
                    (
                        "Acceptance has not been confirmed.",
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
                trade_plan=self._extract_trade_plan(
                    risk_result
                ),
            )

        trade_plan = self._extract_trade_plan(
            risk_result
        )

        if trade_plan is None:
            return DecisionResult(
                decision=DirectorDecision.PASS,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Pass because RiskAnalyst did not produce "
                    "a TradePlan."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Trend and acceptance requirements "
                            "were met."
                        ),
                        (
                            "No TradePlan is available for "
                            "authorization."
                        ),
                        *reasons,
                    )
                ),
                warnings=warnings,
                analyst_summary=summary,
            )

        if not trade_plan.valid:
            return DecisionResult(
                decision=DirectorDecision.PASS,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Pass because the TradePlan failed risk "
                    "validation."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "RiskAnalyst produced an invalid "
                            "TradePlan."
                        ),
                        *trade_plan.reasons,
                        *reasons,
                    )
                ),
                warnings=self._merge_items(
                    (
                        *warnings,
                        *trade_plan.warnings,
                    )
                ),
                analyst_summary=summary,
                trade_plan=trade_plan,
            )

        if not trade_plan.actionable:
            return DecisionResult(
                decision=DirectorDecision.PASS,
                actionable=False,
                confidence=registry.confidence(),
                recommendation=(
                    "Pass because the validated TradePlan is not "
                    "currently actionable."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "The TradePlan does not authorize "
                            "execution."
                        ),
                        *trade_plan.reasons,
                        *reasons,
                    )
                ),
                warnings=self._merge_items(
                    (
                        *warnings,
                        *trade_plan.warnings,
                    )
                ),
                analyst_summary=summary,
                trade_plan=trade_plan,
            )

        plan_direction = self._trade_plan_direction(
            trade_plan
        )

        intended_direction = (
            plan_direction
            if plan_direction.is_directional
            else trade_direction
        )

        applied_adjustment = (
            self._effective_confluence_adjustment(
                confluence=confluence,
                trade_direction=intended_direction,
            )
        )

        base_confidence = registry.confidence()

        confidence = round(
            min(
                100.0,
                (
                    base_confidence
                    + applied_adjustment
                ),
            ),
            2,
        )

        final_direction_reasons, final_direction_warnings = (
            self._directional_confluence_context(
                confluence=confluence,
                trade_direction=intended_direction,
            )
        )

        reasons = self._merge_items(
            (
                *reasons,
                *final_direction_reasons,
            )
        )

        warnings = self._merge_items(
            (
                *warnings,
                *final_direction_warnings,
            )
        )

        if (
            confidence
            < self.config.minimum_ready_confidence
        ):
            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=confidence,
                recommendation=(
                    "The setup is complete, but combined analyst "
                    "confidence is below the authorization threshold."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Combined confidence is "
                            f"{confidence:.0f}."
                        ),
                        (
                            "Required confidence is "
                            f"{self.config.minimum_ready_confidence:.0f}."
                        ),
                        (
                            "Applied institutional confidence "
                            f"adjustment is +{applied_adjustment:.0f}."
                        ),
                        *trade_plan.reasons,
                        *reasons,
                    )
                ),
                warnings=self._merge_items(
                    (
                        *warnings,
                        *trade_plan.warnings,
                    )
                ),
                analyst_summary=summary,
                trade_plan=trade_plan,
            )

        return DecisionResult(
            decision=DirectorDecision.READY,
            actionable=True,
            confidence=confidence,
            recommendation=(
                "Prepare to execute the attached validated "
                "TradePlan."
            ),
            reasons=self._merge_items(
                (
                    "All required analysts have reported.",
                    "Directional trend is confirmed.",
                    (
                        "Setup lifecycle requirements are "
                        "satisfied."
                    ),
                    (
                        "Completed-candle acceptance is "
                        "confirmed."
                    ),
                    (
                        "RiskAnalyst produced an actionable "
                        "TradePlan."
                    ),
                    (
                        "Institutional confluence score is "
                        f"{confluence.score:.0f}/100."
                    ),
                    (
                        "Institutional dominant direction is "
                        f"{confluence.dominant_direction.value}."
                    ),
                    (
                        "Institutional agreement count is "
                        f"{confluence.agreement_count}."
                    ),
                    (
                        "Institutional conflict count is "
                        f"{confluence.conflict_count}."
                    ),
                    (
                        "Institutional confidence adjustment is "
                        f"+{applied_adjustment:.0f}."
                    ),
                    (
                        "Available institutional confidence "
                        "adjustment is "
                        f"+{confluence.confidence_adjustment:.0f}."
                    ),
                    (
                        "Applied institutional confidence "
                        f"adjustment is +{applied_adjustment:.0f}."
                    ),
                    *trade_plan.reasons,
                    *reasons,
                )
            ),
            warnings=self._merge_items(
                (
                    *warnings,
                    *trade_plan.warnings,
                )
            ),
            analyst_summary=summary,
            trade_plan=trade_plan,
        )

    def _missing_required_analysts(
        self,
        registry: AnalystRegistry,
    ) -> tuple[str, ...]:
        return tuple(
            analyst_id
            for analyst_id in CORE_ANALYST_IDS
            if not registry.contains(
                analyst_id
            )
        )

    def _disabled_required_analysts(
        self,
        registry: AnalystRegistry,
    ) -> tuple[str, ...]:
        disabled: list[str] = []

        for analyst_id in CORE_ANALYST_IDS:
            result = registry.get(
                analyst_id
            )

            if (
                result is not None
                and not result.enabled
            ):
                disabled.append(
                    analyst_id
                )

        return tuple(
            disabled
        )

    @staticmethod
    def _require(
        registry: AnalystRegistry,
        analyst_id: str,
    ) -> AnalystResult:
        result = registry.get(
            analyst_id
        )

        if result is None:
            raise RuntimeError(
                "Required analyst result is missing: "
                f"{analyst_id}."
            )

        return result

    @staticmethod
    def _extract_trade_plan(
        risk_result: AnalystResult,
    ) -> TradePlan | None:
        payload = risk_result.payload

        if isinstance(
            payload,
            TradePlan,
        ):
            return payload

        return None

    def _acceptance_confirmed(
        self,
        acceptance_result: AnalystResult,
    ) -> bool:
        payload = acceptance_result.payload

        accepted = getattr(
            payload,
            "accepted",
            None,
        )

        if isinstance(
            accepted,
            bool,
        ):
            return accepted

        opinion = self._normalize(
            acceptance_result.opinion
        )

        return opinion not in {
            "",
            "NONE",
            "NOT_ACCEPTED",
            "REJECTED",
            "WAIT",
        }

    @staticmethod
    def _build_summary(
        registry: AnalystRegistry,
    ) -> dict[str, dict[str, object]]:
        return {
            result.analyst_id: {
                "opinion": result.opinion,
                "confidence": result.confidence,
                "enabled": result.enabled,
            }
            for result in registry.all()
        }

    def _collect_evidence(
        self,
        registry: AnalystRegistry,
    ) -> tuple[str, ...]:
        return self._merge_items(
            registry.evidence()
        )

    def _collect_warnings(
        self,
        registry: AnalystRegistry,
    ) -> tuple[str, ...]:
        return self._merge_items(
            registry.warnings()
        )

    def _trend_direction(
        self,
        trend_result: AnalystResult,
    ) -> InstitutionalDirection:
        opinion = self._normalize(
            trend_result.opinion
        )

        if opinion == self._normalize(
            TREND_BULLISH
        ):
            return InstitutionalDirection.BULLISH

        if opinion == self._normalize(
            TREND_BEARISH
        ):
            return InstitutionalDirection.BEARISH

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _trade_plan_direction(
        trade_plan: TradePlan,
    ) -> InstitutionalDirection:
        direction = getattr(
            trade_plan,
            "direction",
            None,
        )

        return InstitutionalDirection.from_value(
            direction
        )

    @staticmethod
    def _effective_confluence_adjustment(
        *,
        confluence: InstitutionalConfluence,
        trade_direction: InstitutionalDirection,
    ) -> float:
        if not trade_direction.is_directional:
            return 0.0

        if not confluence.dominant_direction.is_directional:
            return 0.0

        if not confluence.dominant_direction.aligns_with(
            trade_direction
        ):
            return 0.0

        return confluence.confidence_adjustment

    @staticmethod
    def _directional_confluence_context(
        *,
        confluence: InstitutionalConfluence,
        trade_direction: InstitutionalDirection,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
    ]:
        reasons: list[str] = []
        warnings: list[str] = []

        if not trade_direction.is_directional:
            return (), ()

        if (
            confluence.dominant_direction
            is InstitutionalDirection.UNKNOWN
        ):
            warnings.append(
                "Institutional direction is unresolved; no "
                "directional confluence bonus is available."
            )

        elif (
            confluence.dominant_direction
            is InstitutionalDirection.NEUTRAL
        ):
            warnings.append(
                "Institutional direction is neutral; no "
                "directional confluence bonus is available."
            )

        elif confluence.dominant_direction.aligns_with(
            trade_direction
        ):
            reasons.append(
                "Institutional confluence aligns with the intended "
                f"{trade_direction.value.lower()} trade."
            )

        elif confluence.dominant_direction.opposes(
            trade_direction
        ):
            warnings.append(
                "Institutional confluence opposes the intended "
                f"{trade_direction.value.lower()} trade."
            )

        if confluence.conflict_count > 0:
            warnings.append(
                "Institutional conflict is present within the "
                "confluence result."
            )

        return (
            DecisionDirector._merge_items(
                reasons
            ),
            DecisionDirector._merge_items(
                warnings
            ),
        )

    def _order_block_support(
        self,
        result: AnalystResult | None,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
    ]:
        if result is None:
            return (), ()

        if not result.enabled:
            return (), ()

        opinion = self._normalize(
            result.opinion
        )

        evidence: tuple[str, ...] = (
            (
                "Order Block Analyst: "
                f"{result.opinion}."
            ),
        )

        warnings: tuple[str, ...] = ()

        if "SUPPLY" in opinion:
            warnings = (
                "Institutional supply is nearby.",
            )

        elif "DEMAND" in opinion:
            evidence = (
                *evidence,
                "Institutional demand supports the setup.",
            )

        return evidence, warnings

    def _liquidity_support(
        self,
        result: AnalystResult | None,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
    ]:
        if result is None:
            return (), ()

        if not result.enabled:
            return (), ()

        opinion = self._normalize(
            result.opinion
        )

        evidence: tuple[str, ...] = (
            (
                "Liquidity Analyst: "
                f"{result.opinion}."
            ),
        )

        warnings: tuple[str, ...] = ()

        if "SUPPLY" in opinion:
            warnings = (
                "Institutional liquidity supply is nearby.",
            )

        elif "DEMAND" in opinion:
            evidence = (
                *evidence,
                (
                    "Institutional liquidity demand supports "
                    "the setup."
                ),
            )

        return evidence, warnings

    @staticmethod
    def _average_confidence(
        *results: AnalystResult,
    ) -> float:
        if not results:
            return 0.0

        return round(
            (
                sum(
                    result.confidence
                    for result in results
                )
                / len(results)
            ),
            2,
        )

    def _wait_recommendation(
        self,
        lifecycle: str,
    ) -> str:
        recommendations = {
            self._normalize(
                LIFECYCLE_DISCOVERY
            ): (
                "Monitor the market while a directional "
                "setup develops."
            ),
            self._normalize(
                LIFECYCLE_TRENDING
            ): (
                "Wait for price to become extended and begin "
                "a controlled return toward Core."
            ),
            self._normalize(
                LIFECYCLE_EXTENDED
            ): (
                "Wait for price to return toward Core. "
                "Do not chase the extension."
            ),
        }

        return recommendations.get(
            lifecycle,
            "Wait for the setup lifecycle to progress.",
        )

    @staticmethod
    def _merge_items(
        items,
    ) -> tuple[str, ...]:
        merged: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(
                item
            ).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(
                key
            )

            merged.append(
                text
            )

        return tuple(
            merged
        )

    @staticmethod
    def _normalize(
        value: object,
    ) -> str:
        enum_value = getattr(
            value,
            "value",
            value,
        )

        return str(
            enum_value
        ).strip().upper()