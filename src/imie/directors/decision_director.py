from __future__ import annotations

from dataclasses import dataclass

from imie.directors.institutional_confluence_engine import (
    InstitutionalConfluenceEngine,
)
from imie.directors.institutional_bias_engine import (
    InstitutionalBiasEngine,
)
from imie.directors.market_phase_engine import (
    MarketPhaseEngine,
)

from imie.models import (
    AcceptanceResult,
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    DecisionResult,
    DirectorDecision,
    InstitutionalConfluence,
    InstitutionalDecisionContext,
    InstitutionalDirection,
    SetupLifecycle,
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
    ANALYST_AUCTION,
    ANALYST_PARTICIPATION,
    ANALYST_PRESSURE,
    ANALYST_VALUE,
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


@dataclass(frozen=True)
class DecisionDirectorConfig:
    """
    Configuration for final trade authorization.
    """

    minimum_ready_confidence: float = 60.0
    institutional_bias_policy: str = "PREPARE"
    confluence_policy: str = "ADVISORY"
    market_phase_policy: str = "ADVISORY"

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_ready_confidence <= 100.0:
            raise ValueError(
                "minimum_ready_confidence must be between 0 and 100."
            )

        normalized_bias_policy = (
            self.institutional_bias_policy
            .strip()
            .upper()
        )

        allowed_bias_policies = {
            "READY",
            "PREPARE",
            "PASS",
        }

        if normalized_bias_policy not in allowed_bias_policies:
            raise ValueError(
                "institutional_bias_policy must be "
                "READY, PREPARE, or PASS."
            )

        normalized_phase_policy = (
            self.market_phase_policy
            .strip()
            .upper()
        )

        allowed_phase_policies = {
            "ADVISORY",
            "PREPARE",
            "PASS",
        }

        normalized_confluence_policy = (
            self.confluence_policy
            .strip()
            .upper()
        )

        allowed_confluence_policies = {
            "ADVISORY",
            "READY",
            "PREPARE",
            "PASS",
        }

        if (
            normalized_confluence_policy
            not in allowed_confluence_policies
        ):
            raise ValueError(
                "confluence_policy must be "
                "ADVISORY, READY, PREPARE, or PASS."
            )

        if normalized_phase_policy not in allowed_phase_policies:
            raise ValueError(
                "market_phase_policy must be "
                "ADVISORY, PREPARE, or PASS."
            )

        object.__setattr__(
            self,
            "institutional_bias_policy",
            normalized_bias_policy,
        )

        object.__setattr__(
            self,
            "confluence_policy",
            normalized_confluence_policy,
        )

        object.__setattr__(
            self,
            "market_phase_policy",
            normalized_phase_policy,
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
        confluence_engine: InstitutionalConfluenceEngine | None = None,
        bias_engine: InstitutionalBiasEngine | None = None,
        market_phase_engine: MarketPhaseEngine | None = None,
    ) -> None:
        self.config = config or DecisionDirectorConfig()

        self.confluence_engine = (
            confluence_engine
            or InstitutionalConfluenceEngine()
        )

        self.bias_engine = (
            bias_engine
            or InstitutionalBiasEngine()
        )

        self.market_phase_engine = (
            market_phase_engine
            or MarketPhaseEngine()
        )

        if not isinstance(
            self.confluence_engine,
            InstitutionalConfluenceEngine,
        ):
            raise TypeError(
                "confluence_engine must be an "
                "InstitutionalConfluenceEngine."
            )

        if not isinstance(
            self.bias_engine,
            InstitutionalBiasEngine,
        ):
            raise TypeError(
                "bias_engine must be an "
                "InstitutionalBiasEngine."
            )

        if not isinstance(
            self.market_phase_engine,
            MarketPhaseEngine,
        ):
            raise TypeError(
                "market_phase_engine must be a "
                "MarketPhaseEngine."
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

        auction_result = registry.get(
            ANALYST_AUCTION
        )

        pressure_result = registry.get(
            ANALYST_PRESSURE
        )

        participation_result = registry.get(
            ANALYST_PARTICIPATION
        )

        value_result = registry.get(
            ANALYST_VALUE
        )

        bias = self.bias_engine.evaluate(
            trend=trend_result,
            structure=structure_result,
            liquidity=liquidity_result,
            order_block=order_block_result,
            auction=auction_result,
            pressure=pressure_result,
            participation=participation_result,
            value=value_result,
        )

        market_phase = self.market_phase_engine.evaluate(
            trend=trend_result,
            structure=structure_result,
            liquidity=liquidity_result,
            order_block=order_block_result,
            auction=auction_result,
            pressure=pressure_result,
            participation=participation_result,
            value=value_result,
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
            auction=auction_result,
            pressure=pressure_result,
            participation=participation_result,
            value=value_result,
        )

        available_trade_plan = self._extract_trade_plan(
            risk_result
        )

        institutional_context = None

        if available_trade_plan is not None:
            institutional_context = (
                self._build_institutional_context(
                    bias=bias,
                    confluence=confluence,
                    market_phase=market_phase,
                    trend_result=trend_result,
                    setup_result=setup_result,
                    acceptance_result=acceptance_result,
                    trade_plan=available_trade_plan,
                )
            )

        reasons = self._merge_items(
            (
                *reasons,
                *order_block_evidence,
                *liquidity_evidence,
                *confluence.evidence,
                *bias.evidence,
                *market_phase.evidence,
                (
                    "Institutional bias is "
                    f"{bias.direction.value}."
                ),
                (
                    "Institutional bias confidence is "
                    f"{bias.confidence:.0f}%."
                ),
                (
                    "Market phase is "
                    f"{market_phase.phase.value}."
                ),
                (
                    "Market phase confidence is "
                    f"{market_phase.confidence:.0f}%."
                ),
                (
                    "Market phase strength is "
                    f"{market_phase.strength:.0f}."
                ),
                (
                    "Market phase agreement count is "
                    f"{market_phase.agreement_count}."
                ),
                (
                    "Market phase conflict count is "
                    f"{market_phase.conflict_count}."
                ),
            )
        )

        warnings = self._merge_items(
            (
                *warnings,
                *order_block_warnings,
                *liquidity_warnings,
                *confluence.warnings,
                *bias.warnings,
                *market_phase.warnings,
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
                trade_plan=available_trade_plan,
                institutional_context=institutional_context,
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
                trade_plan=available_trade_plan,
                institutional_context=institutional_context,
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
                trade_plan=available_trade_plan,
                institutional_context=institutional_context,
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
                trade_plan=available_trade_plan,
                institutional_context=institutional_context,
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
                institutional_context=institutional_context,
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
                institutional_context=institutional_context,
            )

       
        plan_direction = self._trade_plan_direction(
            trade_plan
        )

        intended_direction = (
            plan_direction
            if plan_direction.is_directional
            else trade_direction
        )

        (
            phase_aligned,
            phase_reasons,
            phase_warnings,
        ) = self._market_phase_alignment(
            phase=market_phase.phase,
            trade_direction=intended_direction,
        )

        bias_aligned, bias_reasons, bias_warnings = (
            self._bias_alignment(
                bias_direction=bias.direction,
                trade_direction=intended_direction,
            )
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

        reasons = self._merge_items(
            (
                *reasons,
                *bias_reasons,
                *phase_reasons,
            )
        )

        warnings = self._merge_items(
            (
                *warnings,
                *bias_warnings,
                *phase_warnings,
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
                institutional_context=institutional_context,
            )

        if (
            not bias_aligned
            and self.config.institutional_bias_policy
            != "READY"
        ):
            downgrade_reason = (
                "Trade authorization was reduced because "
                "institutional bias opposes the intended "
                f"{intended_direction.value.lower()} direction."
            )

            if (
                self.config.institutional_bias_policy
                == "PASS"
            ):
                return DecisionResult(
                    decision=DirectorDecision.PASS,
                    actionable=False,
                    confidence=confidence,
                    recommendation=(
                        "Pass because the intended trade direction "
                        "opposes the dominant institutional bias."
                    ),
                    reasons=self._merge_items(
                        (
                            downgrade_reason,
                            (
                                "Institutional bias is "
                                f"{bias.direction.value}."
                            ),
                            (
                                "Intended trade direction is "
                                f"{intended_direction.value}."
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
                    institutional_context=institutional_context,
                )

            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=confidence,
                recommendation=(
                    "The setup is technically complete, but wait "
                    "because institutional bias opposes the intended "
                    "trade direction."
                ),
                reasons=self._merge_items(
                    (
                        downgrade_reason,
                        "Institutional bias policy is PREPARE.",
                        (
                            "Institutional bias is "
                            f"{bias.direction.value}."
                        ),
                        (
                            "Intended trade direction is "
                            f"{intended_direction.value}."
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
                institutional_context=institutional_context,
            )

        confluence_aligned = self._confluence_alignment(
            confluence=confluence,
            trade_direction=intended_direction,
        )

        if (
            confluence_aligned is False
            and self.config.confluence_policy
            not in {
                "ADVISORY",
                "READY",
            }
        ):
            confluence_reason = (
                "Trade authorization was reduced because "
                "institutional confluence opposes the intended "
                f"{intended_direction.value.lower()} direction."
            )

            if (
                self.config.confluence_policy == "PASS"
                and self._strong_confluence_opposition(
                    confluence
                )
            ):
                return DecisionResult(
                    decision=DirectorDecision.PASS,
                    actionable=False,
                    confidence=confidence,
                    recommendation=(
                        "Pass because strong institutional "
                        "confluence opposes the intended trade "
                        "direction."
                    ),
                    reasons=self._merge_items(
                        (
                            confluence_reason,
                            "Confluence policy is PASS.",
                            (
                                "Institutional confluence score is "
                                f"{confluence.score:.0f}/100."
                            ),
                            (
                                "Institutional agreement count is "
                                f"{confluence.agreement_count}."
                            ),
                            (
                                "Institutional conflict count is "
                                f"{confluence.conflict_count}."
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
                    institutional_context=institutional_context,
                )

            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=confidence,
                recommendation=(
                    "The setup is technically complete, but wait "
                    "because institutional confluence opposes the "
                    "intended trade direction."
                ),
                reasons=self._merge_items(
                    (
                        confluence_reason,
                        (
                            "Confluence policy is "
                            f"{self.config.confluence_policy}."
                        ),
                        (
                            "Institutional confluence score is "
                            f"{confluence.score:.0f}/100."
                        ),
                        (
                            "Institutional agreement count is "
                            f"{confluence.agreement_count}."
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
                institutional_context=institutional_context,
            )


        if (
            phase_aligned is not True
            and self.config.market_phase_policy
            != "ADVISORY"
        ):
            phase_value = market_phase.phase.value

            if phase_aligned is None:
                return DecisionResult(
                    decision=DirectorDecision.PREPARE,
                    actionable=False,
                    confidence=confidence,
                    recommendation=(
                        "The setup is technically complete, but wait "
                        "for the market phase to become sufficiently "
                        "resolved before execution."
                    ),
                    reasons=self._merge_items(
                        (
                            (
                                "Trade authorization was reduced "
                                "because market phase compatibility "
                                "is unresolved."
                            ),
                            (
                                "Market phase is "
                                f"{phase_value}."
                            ),
                            (
                                "Market phase policy is "
                                f"{self.config.market_phase_policy}."
                            ),
                            *trade_plan.reasons,
                            *reasons,
                        )
                    ),
                    warnings=self._merge_items(
                        (
                            *warnings,
                            (
                                "An unresolved or transitional market "
                                "phase cannot authorize immediate "
                                "execution."
                            ),
                            *trade_plan.warnings,
                        )
                    ),
                    analyst_summary=summary,
                    trade_plan=trade_plan,
                    institutional_context=institutional_context,
                )

            if (
                self.config.market_phase_policy
                == "PASS"
            ):
                return DecisionResult(
                    decision=DirectorDecision.PASS,
                    actionable=False,
                    confidence=confidence,
                    recommendation=(
                        "Pass because the current market phase "
                        "opposes the intended trade direction."
                    ),
                    reasons=self._merge_items(
                        (
                            (
                                "Trade authorization was rejected "
                                "because the market phase opposes "
                                "the intended direction."
                            ),
                            (
                                "Market phase is "
                                f"{phase_value}."
                            ),
                            (
                                "Intended trade direction is "
                                f"{intended_direction.value}."
                            ),
                            (
                                "Market phase policy is PASS."
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
                    institutional_context=institutional_context,
                )

            return DecisionResult(
                decision=DirectorDecision.PREPARE,
                actionable=False,
                confidence=confidence,
                recommendation=(
                    "The setup is technically complete, but wait "
                    "because the current market phase opposes the "
                    "intended trade direction."
                ),
                reasons=self._merge_items(
                    (
                        (
                            "Trade authorization was reduced "
                            "because the market phase opposes "
                            "the intended direction."
                        ),
                        (
                            "Market phase is "
                            f"{phase_value}."
                        ),
                        (
                            "Intended trade direction is "
                            f"{intended_direction.value}."
                        ),
                        (
                            "Market phase policy is PREPARE."
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
                institutional_context=institutional_context,
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
                    (
                        "Institutional bias alignment is "
                        f"{'aligned' if bias_aligned else 'opposed'}."
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
            institutional_context=institutional_context,
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
    
    @staticmethod
    def _build_institutional_context(
        *,
        bias,
        confluence: InstitutionalConfluence,
        market_phase,
        trend_result: AnalystResult,
        setup_result: AnalystResult,
        acceptance_result: AnalystResult,
        trade_plan: TradePlan,
    ) -> InstitutionalDecisionContext | None:
        setup_payload = setup_result.payload
        acceptance_payload = acceptance_result.payload

        if not isinstance(
            setup_payload,
            SetupLifecycle,
        ):
            return None

        if not isinstance(
            acceptance_payload,
            AcceptanceResult,
        ):
            return None

        return InstitutionalDecisionContext(
            institutional_bias=bias,
            institutional_confluence=confluence,
            market_phase=market_phase,
            trend=trend_result,
            setup_lifecycle=setup_payload,
            acceptance=acceptance_payload,
            risk=trade_plan,
        )

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


    def _bias_alignment(
        self,
        *,
        bias_direction: InstitutionalDirection,
        trade_direction: InstitutionalDirection,
    ) -> tuple[
        bool,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        """
        Evaluate institutional bias alignment with the
        intended trade direction.
        """

        if not trade_direction.is_directional:
            return (
                True,
                (),
                (),
            )

        if not bias_direction.is_directional:
            return (
                True,
                (),
                (
                    "Institutional bias is unresolved.",
                ),
            )

        if bias_direction.aligns_with(
            trade_direction,
        ):
            return (
                True,
                (
                    (
                        "Institutional bias aligns with the "
                        f"intended {trade_direction.value.lower()} trade."
                    ),
                ),
                (),
            )

        return (
            False,
            (),
            (
                (
                    "Institutional bias opposes the "
                    f"intended {trade_direction.value.lower()} trade."
                ),
            ),
        )
    
    def _market_phase_alignment(
        self,
        *,
        phase,
        trade_direction: InstitutionalDirection,
    ) -> tuple[
        bool | None,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        """
        Evaluate whether the market phase supports the intended trade.

        Returns:
            True  -> aligned
            False -> opposed
            None  -> unresolved/advisory
        """

        if not trade_direction.is_directional:
            return None, (), ()

        phase_value = self._normalize(
            phase
        )

        if phase_value in {
            "UNKNOWN",
            "TRANSITION",
        }:
            return (
                None,
                (),
                (
                    "Market phase is unresolved for trade authorization.",
                ),
            )

        if trade_direction is InstitutionalDirection.BULLISH:
            aligned_phases = {
                "MARKUP",
                "PULLBACK",
                "ACCUMULATION",
            }

            opposed_phases = {
                "MARKDOWN",
                "DISTRIBUTION",
            }

        else:
            aligned_phases = {
                "MARKDOWN",
                "PULLBACK",
                "DISTRIBUTION",
            }

            opposed_phases = {
                "MARKUP",
                "ACCUMULATION",
            }

        if phase_value in aligned_phases:
            return (
                True,
                (
                    (
                        "Market phase aligns with the intended "
                        f"{trade_direction.value.lower()} trade."
                    ),
                ),
                (),
            )

        if phase_value in opposed_phases:
            return (
                False,
                (),
                (
                    (
                        "Market phase opposes the intended "
                        f"{trade_direction.value.lower()} trade."
                    ),
                ),
            )

        return (
            None,
            (),
            (
                (
                    "Market phase compatibility is unresolved for "
                    f"{phase_value}."
                ),
            ),
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
    def _confluence_alignment(
        *,
        confluence: InstitutionalConfluence,
        trade_direction: InstitutionalDirection,
    ) -> bool | None:
        if not trade_direction.is_directional:
            return None

        if not confluence.dominant_direction.is_directional:
            return None

        return confluence.dominant_direction.aligns_with(
            trade_direction
        )

    @staticmethod
    def _strong_confluence_opposition(
        confluence: InstitutionalConfluence,
    ) -> bool:
        if not confluence.dominant_direction.is_directional:
            return False

        if confluence.domain_count == 3:
            return (
                confluence.conflict_count == 0
                and confluence.agreement_count >= 2
                and confluence.score >= 60.0
            )

        return (
            confluence.conflict_count <= 1
            and confluence.agreement_count >= 4
            and confluence.score >= 55.0
        )

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