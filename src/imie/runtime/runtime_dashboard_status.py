from __future__ import annotations

import json

from math import isclose, isfinite

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeDashboardStatus:
    health: RuntimeHealthSummary
    symbol: str
    timeframe: str
    latest_cycle_status: (
        AnalysisCycleStatus | None
    )
    latest_cycle_message: str | None
    latest_cycle_started_at: datetime | None
    latest_cycle_completed_at: datetime | None
    market_session: str | None
    latest_decision: str | None
    latest_error_type: str | None

    decision_confidence: float | None = None
    decision_actionable: bool | None = None
    decision_recommendation: str | None = None
    decision_reasons: tuple[str, ...] = ()
    decision_warnings: tuple[str, ...] = ()

    analyst_summary: dict[str, dict[str, object]] = field(
        default_factory=dict
    )

    trade_direction: str | None = None
    trade_plan_valid: bool | None = None
    trade_entry: float | None = None
    trade_stop: float | None = None
    trade_target1: float | None = None
    trade_target2: float | None = None
    trade_rr1: float | None = None
    trade_rr2: float | None = None
    trade_quality: int | None = None
    trade_narrative: str | None = None
    trade_reasons: tuple[str, ...] = ()
    trade_warnings: tuple[str, ...] = ()

    institutional_bias: str | None = None
    institutional_bias_confidence: float | None = None
    institutional_bias_strength: float | None = None
    institutional_bias_bullish_score: float | None = None
    institutional_bias_bearish_score: float | None = None
    institutional_bias_agreement_count: int | None = None
    institutional_bias_conflict_count: int | None = None
    institutional_bias_supporting_domains: tuple[str, ...] = ()
    institutional_bias_opposing_domains: tuple[str, ...] = ()


    confluence_direction: str | None = None
    confluence_score: float | None = None
    confluence_agreement_count: int | None = None
    confluence_conflict_count: int | None = None
    confluence_confidence_adjustment: float | None = None
    confluence_structure_support: bool | None = None
    confluence_liquidity_support: bool | None = None
    confluence_order_block_support: bool | None = None
    confluence_auction_support: bool | None = None
    confluence_pressure_support: bool | None = None
    confluence_participation_support: bool | None = None
    confluence_value_support: bool | None = None
    confluence_bullish_count: int | None = None
    confluence_bearish_count: int | None = None
    confluence_neutral_count: int | None = None
    confluence_unknown_count: int | None = None
    confluence_domain_count: int | None = None

    market_phase: str | None = None
    market_phase_confidence: float | None = None
    market_phase_strength: float | None = None
    market_phase_agreement_count: int | None = None
    market_phase_conflict_count: int | None = None
    market_phase_supporting_domains: tuple[str, ...] = ()
    market_phase_opposing_domains: tuple[str, ...] = ()

    setup_lifecycle_state: str | None = None
    setup_lifecycle_direction: str | None = None
    setup_lifecycle_confidence: float | None = None
    setup_lifecycle_atr_distance: float | None = None
    setup_lifecycle_action: str | None = None
    setup_lifecycle_reason: str | None = None

    acceptance_confirmed: bool | None = None
    acceptance_direction: str | None = None
    acceptance_level: str | None = None
    acceptance_score: int | None = None
    acceptance_confidence: float | None = None
    acceptance_trigger_price: float | None = None
    acceptance_previous_level: float | None = None
    acceptance_pullback_low: float | None = None
    acceptance_pullback_high: float | None = None
    acceptance_reason: str | None = None
    acceptance_evidence: tuple[str, ...] = ()
    acceptance_warnings: tuple[str, ...] = ()

    trend_analyst: str | None = None
    trend_opinion: str | None = None
    trend_confidence: float | None = None
    trend_enabled: bool | None = None
    trend_evidence: tuple[str, ...] = ()
    trend_warnings: tuple[str, ...] = ()

    structure_analyst: str | None = None
    structure_opinion: str | None = None
    structure_confidence: float | None = None
    structure_enabled: bool | None = None

    liquidity_analyst: str | None = None
    liquidity_opinion: str | None = None
    liquidity_confidence: float | None = None
    liquidity_enabled: bool | None = None

    order_block_analyst: str | None = None
    order_block_opinion: str | None = None
    order_block_confidence: float | None = None
    order_block_enabled: bool | None = None

    auction_analyst: str | None = None
    auction_opinion: str | None = None
    auction_confidence: float | None = None
    auction_enabled: bool | None = None

    pressure_analyst: str | None = None
    pressure_opinion: str | None = None
    pressure_confidence: float | None = None
    pressure_enabled: bool | None = None

    participation_analyst: str | None = None
    participation_opinion: str | None = None
    participation_confidence: float | None = None
    participation_enabled: bool | None = None

    value_analyst: str | None = None
    value_opinion: str | None = None
    value_confidence: float | None = None
    value_enabled: bool | None = None

    analyst_domain_count: int | None = None
    analyst_enabled_count: int | None = None
    analyst_resolved_count: int | None = None
    analyst_enabled_resolved_count: int | None = None
    analyst_enabled_unresolved_count: int | None = None

    analyst_confidence_count: int | None = None
    analyst_enabled_confidence_count: int | None = None
    analyst_missing_confidence_count: int | None = None
    analyst_enabled_missing_confidence_count: int | None = None
    analyst_average_confidence: float | None = None
    analyst_enabled_average_confidence: float | None = None

    analyst_confidence_coverage_percentage: float | None = None
    analyst_enabled_confidence_coverage_percentage: float | None = None

    analyst_confidence_coverage_state: str | None = None
    analyst_confidence_coverage_message: str | None = None

    analyst_enabled_confidence_coverage_state: str | None = None
    analyst_enabled_confidence_coverage_message: str | None = None

    analyst_coverage_percentage: float | None = None

    analyst_coverage_state: str | None = None
    analyst_coverage_message: str | None = None
    analyst_operational_status: str | None = None
    analyst_operational_message: str | None = None
    analyst_operational_percentage: float | None = None

    position_size_quantity: int | None = None
    position_size_notional: float | None = None
    position_size_risk_budget: float | None = None
    position_size_actual_risk: float | None = None
    position_size_actual_risk_percent: float | None = None
    position_size_risk_percent: float | None = None
    position_size_actionable: bool | None = None
    position_size_warnings: tuple[str, ...] = ()

    execution_candidate_strategy: str | None = None
    execution_candidate_direction: str | None = None
    execution_candidate_quantity: int | None = None
    execution_candidate_entry: float | None = None
    execution_candidate_stop: float | None = None
    execution_candidate_target1: float | None = None
    execution_candidate_target2: float | None = None
    execution_candidate_notional: float | None = None
    execution_candidate_risk_amount: float | None = None
    execution_candidate_valid: bool | None = None
    execution_candidate_actionable: bool | None = None
    execution_candidate_warnings: tuple[str, ...] = ()

    execution_order_intent_side: str | None = None
    execution_order_intent_quantity: int | None = None
    execution_order_intent_order_type: str | None = None
    execution_order_intent_entry_price: float | None = None
    execution_order_intent_stop_price: float | None = None
    execution_order_intent_target1_price: float | None = None
    execution_order_intent_target2_price: float | None = None
    execution_order_intent_time_in_force: str | None = None
    execution_order_intent_valid: bool | None = None
    execution_order_intent_actionable: bool | None = None
    execution_order_intent_warnings: tuple[str, ...] = ()

    broker_submission_broker: str | None = None
    broker_submission_symbol: str | None = None
    broker_submission_side: str | None = None
    broker_submission_quantity: int | None = None
    broker_submission_accepted: bool | None = None
    broker_submission_order_id: str | None = None
    broker_submission_status: str | None = None
    broker_submission_message: str | None = None
    broker_submission_warnings: tuple[str, ...] = ()

    execution_safety_state: str | None = None
    execution_safety_symbol: str | None = None
    execution_safety_order_notional: float | None = None
    execution_safety_risk_amount: float | None = None
    execution_safety_maximum_order_notional: float | None = None
    execution_safety_maximum_risk_amount: float | None = None
    execution_safety_allowed: bool | None = None
    execution_safety_kill_switch_active: bool | None = None
    execution_safety_violations: tuple[str, ...] = ()
    execution_safety_warnings: tuple[str, ...] = ()
    execution_submission_fingerprint: str | None = None
    execution_submission_reserved_at: str | None = None
    concurrent_position_broker: str | None = None
    concurrent_position_open_count: int | None = None
    concurrent_position_maximum: int | None = None
    concurrent_position_symbol_already_open: bool | None = None
    concurrent_position_allowed: bool | None = None
    concurrent_position_exposure_age_seconds: float | None = None
    concurrent_position_maximum_exposure_age_seconds: float | None = None
    concurrent_position_exposure_fresh: bool | None = None
    concurrent_position_violations: tuple[str, ...] = ()
    daily_loss_broker: str | None = None
    daily_loss_realized_pnl: float | None = None
    daily_loss_unrealized_pnl: float | None = None
    daily_loss_total_pnl: float | None = None
    daily_loss_amount: float | None = None
    daily_loss_maximum: float | None = None
    daily_loss_within_limit: bool | None = None
    daily_loss_allowed: bool | None = None
    daily_loss_violations: tuple[str, ...] = ()

    protected_submission_broker: str | None = None
    protected_submission_quantity: int | None = None
    protected_submission_accepted: bool | None = None
    protected_submission_status: str | None = None
    protected_submission_message: str | None = None
    protected_submission_order_count: int | None = None
    protected_submission_rollback_attempted: bool | None = None
    protected_submission_rollback_succeeded: bool | None = None
    protected_submission_orders: tuple[str, ...] = ()
    protected_submission_warnings: tuple[str, ...] = ()


    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.health,
            RuntimeHealthSummary,
        ):
            raise TypeError(
                "health must be a RuntimeHealthSummary."
            )

        normalized_symbol = (
            self._normalize_required_text(
                field_name="symbol",
                value=self.symbol,
            )
        )

        normalized_timeframe = (
            self._normalize_required_text(
                field_name="timeframe",
                value=self.timeframe,
            )
        )

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol.upper(),
        )

        object.__setattr__(
            self,
            "timeframe",
            normalized_timeframe.lower(),
        )

        if (
            self.latest_cycle_status
            is not None
            and not isinstance(
                self.latest_cycle_status,
                AnalysisCycleStatus,
            )
        ):
            raise TypeError(
                "latest_cycle_status must be an "
                "AnalysisCycleStatus or None."
            )

        if (
            self.decision_confidence
            is not None
        ):
            if (
                isinstance(
                    self.decision_confidence,
                    bool,
                )
                or not isinstance(
                    self.decision_confidence,
                    int | float,
                )
            ):
                raise TypeError(
                    "decision_confidence must be "
                    "a number or None."
                )

            normalized_confidence = float(
                self.decision_confidence
            )

            if not (
                0.0
                <= normalized_confidence
                <= 100.0
            ):
                raise ValueError(
                    "decision_confidence must be "
                    "between 0 and 100."
                )

            object.__setattr__(
                self,
                "decision_confidence",
                normalized_confidence,
            )

        if (
            self.confluence_confidence_adjustment
            is not None
        ):
            value = (
                self.confluence_confidence_adjustment
            )

            if (
                isinstance(
                    value,
                    bool,
                )
                or not isinstance(
                    value,
                    int | float,
                )
            ):
                raise TypeError(
                    "confluence_confidence_adjustment "
                    "must be a number or None."
                )

            normalized = float(
                value
            )

            if not (
                0.0
                <= normalized
                <= 8.0
            ):
                raise ValueError(
                    "confluence_confidence_adjustment "
                    "must be between 0 and 8."
                )

            object.__setattr__(
                self,
                "confluence_confidence_adjustment",
                normalized,
            )

        for field_name in (
            "confluence_structure_support",
            "confluence_liquidity_support",
            "confluence_order_block_support",
            "confluence_auction_support",
            "confluence_pressure_support",
            "confluence_participation_support",
            "confluence_value_support",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    bool,
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "a bool or None."
                )

        for field_name in (
            "institutional_bias_confidence",
            "institutional_bias_strength",
            "institutional_bias_bullish_score",
            "institutional_bias_bearish_score",
            "market_phase_confidence",
            "market_phase_strength",
            "confluence_score",
            "acceptance_confidence",
            "trend_confidence",
            "structure_confidence",
            "liquidity_confidence",
            "order_block_confidence",
            "auction_confidence",
            "pressure_confidence",
            "participation_confidence",
            "value_confidence",
            "analyst_average_confidence",
            "analyst_enabled_average_confidence",
            "analyst_confidence_coverage_percentage",
            "analyst_enabled_confidence_coverage_percentage",
            "analyst_coverage_percentage",
            "analyst_operational_percentage",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is None:
                continue

            if (
                isinstance(
                    value,
                    bool,
                )
                or not isinstance(
                    value,
                    (int, float),
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "a number or None."
                )

            if not isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite."
                )

            normalized = float(
                value
            )

            if normalized == 0.0:
                normalized = 0.0

            if not (
                0.0
                <= normalized
                <= 100.0
            ):
                raise ValueError(
                    f"{field_name} must be "
                    "between 0 and 100."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        for field_name in (
            "execution_candidate_valid",
            "execution_candidate_actionable",
            "execution_order_intent_valid",
            "execution_order_intent_actionable",
            "broker_submission_accepted",
            "execution_safety_allowed",
            "execution_safety_kill_switch_active",
            "concurrent_position_symbol_already_open",
            "concurrent_position_allowed",
            "concurrent_position_exposure_fresh",
            "daily_loss_within_limit",
            "daily_loss_allowed",
            "protected_submission_accepted",
            "protected_submission_rollback_attempted",
            "protected_submission_rollback_succeeded",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    bool,
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "a bool or None."
                )

        for field_name in (
            "confluence_agreement_count",
            "confluence_conflict_count",
            "market_phase_agreement_count",
            "market_phase_conflict_count",
            "institutional_bias_agreement_count",
            "institutional_bias_conflict_count",
            "confluence_bullish_count",
            "confluence_bearish_count",
            "confluence_neutral_count",
            "confluence_unknown_count",
            "confluence_domain_count",
            "analyst_domain_count",
            "analyst_enabled_count",
            "analyst_resolved_count",
            "analyst_enabled_resolved_count",
            "analyst_enabled_unresolved_count",
            "analyst_confidence_count",
            "analyst_enabled_confidence_count",
            "analyst_missing_confidence_count",
            "analyst_enabled_missing_confidence_count",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is None:
                continue

            if (
                isinstance(
                    value,
                    bool,
                )
                or not isinstance(
                    value,
                    int,
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "an int or None."
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        if (
            self.analyst_domain_count is not None
            and self.analyst_confidence_count is not None
            and self.analyst_confidence_count
            > self.analyst_domain_count
        ):
            raise ValueError(
                "analyst_confidence_count cannot exceed "
                "analyst_domain_count."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_missing_confidence_count
            is not None
            and self.analyst_missing_confidence_count
            > self.analyst_domain_count
        ):
            raise ValueError(
                "analyst_missing_confidence_count cannot "
                "exceed analyst_domain_count."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_missing_confidence_count
            is not None
            and self.analyst_enabled_missing_confidence_count
            > self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst_enabled_missing_confidence_count "
                "cannot exceed analyst_enabled_count."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_confidence_count
            is not None
            and self.analyst_enabled_confidence_count
            > self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst_enabled_confidence_count cannot "
                "exceed analyst_enabled_count."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_confidence_count is not None
            and self.analyst_missing_confidence_count
            is not None
            and (
                self.analyst_confidence_count
                + self.analyst_missing_confidence_count
            )
            != self.analyst_domain_count
        ):
            raise ValueError(
                "analyst confidence and missing confidence "
                "counts must equal analyst_domain_count."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_confidence_count
            is not None
            and self.analyst_enabled_missing_confidence_count
            is not None
            and (
                self.analyst_enabled_confidence_count
                + self.analyst_enabled_missing_confidence_count
            )
            != self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst enabled confidence and missing "
                "confidence counts must equal "
                "analyst_enabled_count."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_enabled_count is not None
            and self.analyst_enabled_count
            > self.analyst_domain_count
        ):
            raise ValueError(
                "analyst_enabled_count cannot exceed "
                "analyst_domain_count."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_resolved_count is not None
            and self.analyst_resolved_count
            > self.analyst_domain_count
        ):
            raise ValueError(
                "analyst_resolved_count cannot exceed "
                "analyst_domain_count."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_resolved_count
            > self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst_enabled_resolved_count cannot "
                "exceed analyst_enabled_count."
            )

        if (
            self.analyst_resolved_count is not None
            and self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_resolved_count
            > self.analyst_resolved_count
        ):
            raise ValueError(
                "analyst_enabled_resolved_count cannot "
                "exceed analyst_resolved_count."
            )

        if (
            self.analyst_confidence_count is not None
            and self.analyst_enabled_confidence_count
            is not None
            and self.analyst_enabled_confidence_count
            > self.analyst_confidence_count
        ):
            raise ValueError(
                "analyst_enabled_confidence_count cannot "
                "exceed analyst_confidence_count."
            )

        if (
            self.analyst_missing_confidence_count
            is not None
            and self.analyst_enabled_missing_confidence_count
            is not None
            and self.analyst_enabled_missing_confidence_count
            > self.analyst_missing_confidence_count
        ):
            raise ValueError(
                "analyst_enabled_missing_confidence_count "
                "cannot exceed "
                "analyst_missing_confidence_count."
            )

        if (
            self.analyst_confidence_count == 0
            and self.analyst_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_average_confidence must be None "
                "when analyst_confidence_count is zero."
            )

        if (
            self.analyst_enabled_confidence_count == 0
            and self.analyst_enabled_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_enabled_average_confidence must be "
                "None when "
                "analyst_enabled_confidence_count is zero."
            )

        if (
            self.analyst_confidence_coverage_state
            in {
                "UNAVAILABLE",
                "MISSING",
            }
            and self.analyst_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_average_confidence must be None "
                "when analyst_confidence_coverage_state is "
                "UNAVAILABLE or MISSING."
            )

        if (
            self.analyst_enabled_confidence_coverage_state
            in {
                "UNAVAILABLE",
                "DISABLED",
                "MISSING",
            }
            and self.analyst_enabled_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_enabled_average_confidence must be "
                "None when "
                "analyst_enabled_confidence_coverage_state "
                "is UNAVAILABLE, DISABLED, or MISSING."
            )

        if (
            self.analyst_confidence_coverage_state
            is not None
            and self.analyst_confidence_coverage_percentage
            is not None
        ):
            coverage_state = (
                self.analyst_confidence_coverage_state
            )
            coverage_percentage = (
                self.analyst_confidence_coverage_percentage
            )

            if (
                coverage_state
                in {
                    "UNAVAILABLE",
                    "MISSING",
                }
                and not isclose(
                    coverage_percentage,
                    0.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_confidence_coverage_percentage "
                    "must be zero when "
                    "analyst_confidence_coverage_state is "
                    "UNAVAILABLE or MISSING."
                )

            if (
                coverage_state == "PARTIAL"
                and not (
                    0.0
                    < coverage_percentage
                    < 100.0
                )
            ):
                raise ValueError(
                    "analyst_confidence_coverage_percentage "
                    "must be greater than zero and less than "
                    "100 when "
                    "analyst_confidence_coverage_state is "
                    "PARTIAL."
                )

            if (
                coverage_state == "COMPLETE"
                and not isclose(
                    coverage_percentage,
                    100.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_confidence_coverage_percentage "
                    "must be 100 when "
                    "analyst_confidence_coverage_state is "
                    "COMPLETE."
                )

        if (
            self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
        ):
            enabled_coverage_state = (
                self.analyst_enabled_confidence_coverage_state
            )
            enabled_coverage_percentage = (
                self.analyst_enabled_confidence_coverage_percentage
            )

            if (
                enabled_coverage_state
                in {
                    "UNAVAILABLE",
                    "DISABLED",
                    "MISSING",
                }
                and not isclose(
                    enabled_coverage_percentage,
                    0.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_enabled_confidence_coverage_percentage "
                    "must be zero when "
                    "analyst_enabled_confidence_coverage_state "
                    "is UNAVAILABLE, DISABLED, or MISSING."
                )

            if (
                enabled_coverage_state == "PARTIAL"
                and not (
                    0.0
                    < enabled_coverage_percentage
                    < 100.0
                )
            ):
                raise ValueError(
                    "analyst_enabled_confidence_coverage_percentage "
                    "must be greater than zero and less than "
                    "100 when "
                    "analyst_enabled_confidence_coverage_state "
                    "is PARTIAL."
                )

            if (
                enabled_coverage_state == "COMPLETE"
                and not isclose(
                    enabled_coverage_percentage,
                    100.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_enabled_confidence_coverage_percentage "
                    "must be 100 when "
                    "analyst_enabled_confidence_coverage_state "
                    "is COMPLETE."
                )

        if (
            self.analyst_domain_count == 0
            and self.analyst_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_average_confidence must be None "
                "when analyst_domain_count is zero."
            )

        if (
            self.analyst_enabled_count == 0
            and self.analyst_enabled_average_confidence
            is not None
        ):
            raise ValueError(
                "analyst_enabled_average_confidence must be "
                "None when analyst_enabled_count is zero."
            )

        if (
            self.analyst_domain_count == 0
            and self.analyst_confidence_coverage_percentage
            is not None
            and not isclose(
                self.analyst_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_confidence_coverage_percentage "
                "must be zero when analyst_domain_count "
                "is zero."
            )

        if (
            self.analyst_enabled_count == 0
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
            and not isclose(
                self.analyst_enabled_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_percentage "
                "must be zero when analyst_enabled_count "
                "is zero."
            )

        if (
            self.analyst_confidence_count == 0
            and self.analyst_confidence_coverage_percentage
            is not None
            and not isclose(
                self.analyst_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_confidence_coverage_percentage "
                "must be zero when analyst_confidence_count "
                "is zero."
            )

        if (
            self.analyst_enabled_confidence_count == 0
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
            and not isclose(
                self.analyst_enabled_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_percentage "
                "must be zero when "
                "analyst_enabled_confidence_count is zero."
            )

        if (
            self.analyst_confidence_count == 0
            and self.analyst_confidence_coverage_state
            is not None
            and self.analyst_confidence_coverage_state
            not in {
                "UNAVAILABLE",
                "MISSING",
            }
        ):
            raise ValueError(
                "analyst_confidence_coverage_state must be "
                "UNAVAILABLE or MISSING when "
                "analyst_confidence_count is zero."
            )

        if (
            self.analyst_enabled_confidence_count == 0
            and self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_state
            not in {
                "UNAVAILABLE",
                "DISABLED",
                "MISSING",
            }
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_state "
                "must be UNAVAILABLE, DISABLED, or MISSING "
                "when analyst_enabled_confidence_count is zero."
            )

        if (
            self.analyst_confidence_count is not None
            and self.analyst_confidence_count > 0
            and self.analyst_confidence_coverage_state
            is not None
            and self.analyst_confidence_coverage_state
            not in {
                "PARTIAL",
                "COMPLETE",
            }
        ):
            raise ValueError(
                "analyst_confidence_coverage_state must be "
                "PARTIAL or COMPLETE when "
                "analyst_confidence_count is positive."
            )

        if (
            self.analyst_enabled_confidence_count is not None
            and self.analyst_enabled_confidence_count > 0
            and self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_state
            not in {
                "PARTIAL",
                "COMPLETE",
            }
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_state "
                "must be PARTIAL or COMPLETE when "
                "analyst_enabled_confidence_count is positive."
            )

        if (
            self.analyst_confidence_count is not None
            and self.analyst_confidence_count > 0
            and self.analyst_confidence_coverage_percentage
            is not None
            and isclose(
                self.analyst_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_confidence_coverage_percentage "
                "must be greater than zero when "
                "analyst_confidence_count is positive."
            )

        if (
            self.analyst_enabled_confidence_count is not None
            and self.analyst_enabled_confidence_count > 0
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
            and isclose(
                self.analyst_enabled_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_percentage "
                "must be greater than zero when "
                "analyst_enabled_confidence_count is positive."
            )

        if (
            self.analyst_domain_count == 0
            and self.analyst_confidence_coverage_state
            is not None
            and self.analyst_confidence_coverage_state
            != "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_confidence_coverage_state must be "
                "UNAVAILABLE when analyst_domain_count is zero."
            )

        if (
            self.analyst_enabled_count == 0
            and self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_state
            not in {
                "UNAVAILABLE",
                "DISABLED",
            }
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_state "
                "must be UNAVAILABLE or DISABLED when "
                "analyst_enabled_count is zero."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_domain_count > 0
            and self.analyst_enabled_count == 0
            and self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_state
            != "DISABLED"
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_state "
                "must be DISABLED when analyst_domain_count "
                "is positive and analyst_enabled_count is zero."
            )

        if (
            self.analyst_average_confidence is not None
            and self.analyst_confidence_coverage_percentage
            is not None
            and isclose(
                self.analyst_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_confidence_coverage_percentage "
                "must be greater than zero when "
                "analyst_average_confidence is reported."
            )

        if (
            self.analyst_enabled_average_confidence
            is not None
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
            and isclose(
                self.analyst_enabled_confidence_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_percentage "
                "must be greater than zero when "
                "analyst_enabled_average_confidence is reported."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_domain_count > 0
            and self.analyst_confidence_coverage_state
            is not None
            and self.analyst_confidence_coverage_state
            == "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_confidence_coverage_state cannot be "
                "UNAVAILABLE when analyst_domain_count is positive."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_count > 0
            and self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_enabled_confidence_coverage_state
            in {
                "UNAVAILABLE",
                "DISABLED",
            }
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_state "
                "cannot be UNAVAILABLE or DISABLED when "
                "analyst_enabled_count is positive."
            )


        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_unresolved_count
            is not None
            and self.analyst_enabled_unresolved_count
            > self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst_enabled_unresolved_count cannot "
                "exceed analyst_enabled_count."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_unresolved_count
            is not None
            and (
                self.analyst_enabled_resolved_count
                + self.analyst_enabled_unresolved_count
            )
            != self.analyst_enabled_count
        ):
            raise ValueError(
                "analyst enabled resolved and unresolved "
                "counts must equal analyst_enabled_count."
            )

        if (
            self.decision_actionable
            is not None
            and not isinstance(
                self.decision_actionable,
                bool,
            )
        ):
            raise TypeError(
                "decision_actionable must be "
                "a bool or None."
            )

        if (
            self.trade_plan_valid
            is not None
            and not isinstance(
                self.trade_plan_valid,
                bool,
            )
        ):
            raise TypeError(
                "trade_plan_valid must be "
                "a bool or None."
            )
        if (
            self.position_size_actionable
            is not None
            and not isinstance(
                self.position_size_actionable,
                bool,
            )
        ):
            raise TypeError(
                "position_size_actionable must be "
                "a bool or None."
            )

        if (
            self.acceptance_confirmed is not None
            and not isinstance(
                self.acceptance_confirmed,
                bool,
            )
        ):
            raise TypeError(
                "acceptance_confirmed must be "
                "a bool or None."
            )

        if (
            self.trend_enabled is not None
            and not isinstance(
                self.trend_enabled,
                bool,
            )
        ):
            raise TypeError(
                "trend_enabled must be "
                "a bool or None."
            )

        if (
            self.structure_enabled is not None
            and not isinstance(
                self.structure_enabled,
                bool,
            )
        ):
            raise TypeError(
                "structure_enabled must be "
                "a bool or None."
            )

        if (
            self.liquidity_enabled is not None
            and not isinstance(
                self.liquidity_enabled,
                bool,
            )
        ):
            raise TypeError(
                "liquidity_enabled must be "
                "a bool or None."
            )
        if (
            self.order_block_enabled is not None
            and not isinstance(
                self.order_block_enabled,
                bool,
            )
        ):
            raise TypeError(
                "order_block_enabled must be "
                "a bool or None."
            )
        if (
            self.auction_enabled is not None
            and not isinstance(
                self.auction_enabled,
                bool,
            )
        ):
            raise TypeError(
                "auction_enabled must be "
                "a bool or None."
            )
        if (
            self.pressure_enabled is not None
            and not isinstance(
                self.pressure_enabled,
                bool,
            )
        ):
            raise TypeError(
                "pressure_enabled must be "
                "a bool or None."
            )
        if (
            self.participation_enabled is not None
            and not isinstance(
                self.participation_enabled,
                bool,
            )
        ):
            raise TypeError(
                "participation_enabled must be "
                "a bool or None."
            )
        if (
            self.value_enabled is not None
            and not isinstance(
                self.value_enabled,
                bool,
            )
        ):
            raise TypeError(
                "value_enabled must be "
                "a bool or None."
            )

        if (
            self.analyst_coverage_state is not None
            and self.analyst_coverage_state
            not in {
                "UNAVAILABLE",
                "UNRESOLVED",
                "PARTIAL",
                "COMPLETE",
            }
        ):
            raise ValueError(
                "analyst_coverage_state must be one of: "
                "UNAVAILABLE, UNRESOLVED, PARTIAL, COMPLETE."
            )

        if (
            self.analyst_coverage_state is not None
            and self.analyst_coverage_percentage is not None
        ):
            coverage_state = (
                self.analyst_coverage_state
            )
            coverage_percentage = (
                self.analyst_coverage_percentage
            )

            if (
                coverage_state
                in {
                    "UNAVAILABLE",
                    "UNRESOLVED",
                }
                and not isclose(
                    coverage_percentage,
                    0.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_coverage_percentage must be zero "
                    "when analyst_coverage_state is "
                    "UNAVAILABLE or UNRESOLVED."
                )

            if (
                coverage_state == "PARTIAL"
                and not (
                    0.0
                    < coverage_percentage
                    < 100.0
                )
            ):
                raise ValueError(
                    "analyst_coverage_percentage must be greater "
                    "than zero and less than 100 when "
                    "analyst_coverage_state is PARTIAL."
                )

            if (
                coverage_state == "COMPLETE"
                and not isclose(
                    coverage_percentage,
                    100.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_coverage_percentage must be 100 "
                    "when analyst_coverage_state is COMPLETE."
                )

        if (
            self.analyst_domain_count is not None
            and self.analyst_resolved_count is not None
            and self.analyst_coverage_percentage is not None
        ):
            expected_coverage_percentage = (
                (
                    self.analyst_resolved_count
                    / self.analyst_domain_count
                )
                * 100.0
                if self.analyst_domain_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_coverage_percentage,
                expected_coverage_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_coverage_percentage must agree "
                    "with analyst_resolved_count and "
                    "analyst_domain_count."
                )

        if (
            self.analyst_coverage_state is not None
            and self.analyst_domain_count is not None
            and self.analyst_resolved_count is not None
        ):
            if self.analyst_domain_count == 0:
                expected_coverage_state = (
                    "UNAVAILABLE"
                )

            elif self.analyst_resolved_count == 0:
                expected_coverage_state = (
                    "UNRESOLVED"
                )

            elif (
                self.analyst_resolved_count
                < self.analyst_domain_count
            ):
                expected_coverage_state = (
                    "PARTIAL"
                )

            else:
                expected_coverage_state = (
                    "COMPLETE"
                )

            if (
                self.analyst_coverage_state
                != expected_coverage_state
            ):
                raise ValueError(
                    "analyst_coverage_state must agree "
                    "with analyst_domain_count and "
                    "analyst_resolved_count."
                )

        if (
            self.analyst_domain_count is not None
            and self.analyst_confidence_count is not None
            and self.analyst_confidence_coverage_percentage
            is not None
        ):
            expected_percentage = (
                (
                    self.analyst_confidence_count
                    / self.analyst_domain_count
                )
                * 100.0
                if self.analyst_domain_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_confidence_coverage_percentage,
                expected_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_confidence_coverage_percentage "
                    "must agree with analyst_confidence_count "
                    "and analyst_domain_count."
                )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_confidence_count
            is not None
            and self.analyst_enabled_confidence_coverage_percentage
            is not None
        ):
            expected_enabled_percentage = (
                (
                    self.analyst_enabled_confidence_count
                    / self.analyst_enabled_count
                )
                * 100.0
                if self.analyst_enabled_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_enabled_confidence_coverage_percentage,
                expected_enabled_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_enabled_confidence_coverage_percentage "
                    "must agree with "
                    "analyst_enabled_confidence_count and "
                    "analyst_enabled_count."
                )

        for field_name in (
            "analyst_confidence_coverage_state",
            "analyst_enabled_confidence_coverage_state",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and value
                not in {
                    "UNAVAILABLE",
                    "DISABLED",
                    "MISSING",
                    "PARTIAL",
                    "COMPLETE",
                }
            ):
                raise ValueError(
                    f"{field_name} must be one of: "
                    "UNAVAILABLE, DISABLED, MISSING, "
                    "PARTIAL, COMPLETE."
                )

        for field_name in (
            "trade_entry",
            "trade_stop",
            "trade_target1",
            "trade_target2",
            "trade_rr1",
            "trade_rr2",
            "acceptance_trigger_price",
            "acceptance_previous_level",
            "acceptance_pullback_low",
            "acceptance_pullback_high",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is None:
                continue

            if (
                isinstance(
                    value,
                    bool,
                )
                or not isinstance(
                    value,
                    int | float,
                )
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "a number or None."
                )

            object.__setattr__(
                self,
                field_name,
                float(
                    value
                ),
            )

        if (
            self.trade_quality
            is not None
            and (
                isinstance(
                    self.trade_quality,
                    bool,
                )
                or not isinstance(
                    self.trade_quality,
                    int,
                )
            )
        ):
            raise TypeError(
                "trade_quality must be "
                "an int or None."
            )

        if (
            self.acceptance_score is not None
            and (
                isinstance(
                    self.acceptance_score,
                    bool,
                )
                or not isinstance(
                    self.acceptance_score,
                    int,
                )
            )
        ):
            raise TypeError(
                "acceptance_score must be "
                "an int or None."
            )

        if (
            self.acceptance_score is not None
            and not (
                0
                <= self.acceptance_score
                <= 100
            )
        ):
            raise ValueError(
                "acceptance_score must be "
                "between 0 and 100."
            )

        if (
            self.trade_quality
            is not None
            and not (
                0
                <= self.trade_quality
                <= 100
            )
        ):
            raise ValueError(
                "trade_quality must be "
                "between 0 and 100."
            )

        for field_name in (
            "latest_cycle_message",
            "market_session",
            "latest_decision",
            "decision_recommendation",
            "trade_direction",
            "trade_narrative",
            "institutional_bias",
            "market_phase",
            "confluence_direction",
            "setup_lifecycle_state",
            "setup_lifecycle_direction",
            "setup_lifecycle_action",
            "setup_lifecycle_reason",
            "acceptance_direction",
            "acceptance_level",
            "acceptance_reason",
            "trend_analyst",
            "trend_opinion",
            "structure_analyst",
            "structure_opinion",
            "liquidity_analyst",
            "liquidity_opinion",
            "order_block_analyst",
            "order_block_opinion",
            "auction_analyst",
            "auction_opinion",
            "pressure_analyst",
            "pressure_opinion",
            "participation_analyst",
            "participation_opinion",
            "value_analyst",
            "value_opinion",

            "analyst_confidence_coverage_state",
            "analyst_confidence_coverage_message",
            "analyst_enabled_confidence_coverage_state",
            "analyst_enabled_confidence_coverage_message",
            "analyst_coverage_state",
            "analyst_coverage_message",
            "analyst_operational_status",
            "analyst_operational_message",

            "latest_error_type",

        ):
            value = getattr(
                self,
                field_name,
            )

            if value is None:
                continue

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be "
                    "a string or None."
                )

            normalized = value.strip()

            object.__setattr__(
                self,
                field_name,
                normalized or None,
            )

        if (
            self.analyst_confidence_coverage_message
            is not None
            and self.analyst_confidence_coverage_state
            is None
        ):
            raise ValueError(
                "analyst_confidence_coverage_message "
                "requires analyst_confidence_coverage_state."
            )

        if (
            self.analyst_enabled_confidence_coverage_message
            is not None
            and self.analyst_enabled_confidence_coverage_state
            is None
        ):
            raise ValueError(
                "analyst_enabled_confidence_coverage_message "
                "requires "
                "analyst_enabled_confidence_coverage_state."
            )

        if (
            self.analyst_coverage_message is not None
            and self.analyst_coverage_state is None
        ):
            raise ValueError(
                "analyst_coverage_message requires "
                "analyst_coverage_state."
            )

        if (
            self.analyst_operational_message is not None
            and self.analyst_operational_status is None
        ):
            raise ValueError(
                "analyst_operational_message requires "
                "analyst_operational_status."
            )

        if (
            self.analyst_operational_status is not None
            and self.analyst_operational_status
            not in {
                "UNAVAILABLE",
                "DISABLED",
                "UNRESOLVED",
                "DEGRADED",
                "OPERATIONAL",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be one of: "
                "UNAVAILABLE, DISABLED, UNRESOLVED, "
                "DEGRADED, OPERATIONAL."
            )

        if (
            self.analyst_operational_status is not None
            and self.analyst_operational_percentage is not None
        ):
            operational_status = (
                self.analyst_operational_status
            )
            operational_percentage = (
                self.analyst_operational_percentage
            )

            if (
                operational_status
                in {
                    "UNAVAILABLE",
                    "DISABLED",
                    "UNRESOLVED",
                }
                and not isclose(
                    operational_percentage,
                    0.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_operational_percentage must be zero "
                    "when analyst_operational_status is "
                    "UNAVAILABLE, DISABLED, or UNRESOLVED."
                )

            if (
                operational_status == "DEGRADED"
                and not (
                    0.0
                    < operational_percentage
                    < 100.0
                )
            ):
                raise ValueError(
                    "analyst_operational_percentage must be greater "
                    "than zero and less than 100 when "
                    "analyst_operational_status is DEGRADED."
                )

            if (
                operational_status == "OPERATIONAL"
                and not isclose(
                    operational_percentage,
                    100.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError(
                    "analyst_operational_percentage must be 100 "
                    "when analyst_operational_status is OPERATIONAL."
                )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_resolved_count
            is not None
            and self.analyst_operational_percentage
            is not None
        ):
            expected_operational_percentage = (
                (
                    self.analyst_enabled_resolved_count
                    / self.analyst_enabled_count
                )
                * 100.0
                if self.analyst_enabled_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_operational_percentage,
                expected_operational_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_operational_percentage must agree "
                    "with analyst_enabled_resolved_count and "
                    "analyst_enabled_count."
                )

        if (
            self.analyst_operational_status is not None
            and self.analyst_domain_count is not None
            and self.analyst_enabled_count is not None
            and self.analyst_enabled_resolved_count
            is not None
        ):
            if self.analyst_domain_count == 0:
                expected_operational_status = (
                    "UNAVAILABLE"
                )

            elif self.analyst_enabled_count == 0:
                expected_operational_status = (
                    "DISABLED"
                )

            elif self.analyst_enabled_resolved_count == 0:
                expected_operational_status = (
                    "UNRESOLVED"
                )

            elif (
                self.analyst_enabled_resolved_count
                < self.analyst_enabled_count
            ):
                expected_operational_status = (
                    "DEGRADED"
                )

            else:
                expected_operational_status = (
                    "OPERATIONAL"
                )

            if (
                self.analyst_operational_status
                != expected_operational_status
            ):
                raise ValueError(
                    "analyst_operational_status must agree "
                    "with analyst_domain_count, "
                    "analyst_enabled_count, and "
                    "analyst_enabled_resolved_count."
                )

        if (
            self.analyst_domain_count == 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            != "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNAVAILABLE when analyst_domain_count "
                "is zero."
            )

        if (
            self.analyst_enabled_count == 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            not in {
                "UNAVAILABLE",
                "DISABLED",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNAVAILABLE or DISABLED when "
                "analyst_enabled_count is zero."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_domain_count > 0
            and self.analyst_enabled_count == 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            != "DISABLED"
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "DISABLED when analyst_domain_count is "
                "positive and analyst_enabled_count is zero."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_count > 0
            and self.analyst_operational_status
            in {
                "UNAVAILABLE",
                "DISABLED",
            }
        ):
            raise ValueError(
                "analyst_operational_status cannot be "
                "UNAVAILABLE or DISABLED when "
                "analyst_enabled_count is positive."
            )

        if (
            self.analyst_enabled_resolved_count == 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            not in {
                "UNAVAILABLE",
                "DISABLED",
                "UNRESOLVED",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNAVAILABLE, DISABLED, or UNRESOLVED "
                "when analyst_enabled_resolved_count "
                "is zero."
            )

        if (
            self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_resolved_count > 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            not in {
                "DEGRADED",
                "OPERATIONAL",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "DEGRADED or OPERATIONAL when "
                "analyst_enabled_resolved_count "
                "is positive."
            )

        if (
            self.analyst_enabled_count == 0
            and self.analyst_operational_percentage
            is not None
            and not isclose(
                self.analyst_operational_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be zero "
                "when analyst_enabled_count is zero."
            )

        if (
            self.analyst_enabled_resolved_count == 0
            and self.analyst_operational_percentage
            is not None
            and not isclose(
                self.analyst_operational_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be zero "
                "when analyst_enabled_resolved_count is zero."
            )

        if (
            self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_resolved_count > 0
            and self.analyst_operational_percentage
            is not None
            and isclose(
                self.analyst_operational_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be "
                "greater than zero when "
                "analyst_enabled_resolved_count is positive."
            )

        if (
            self.analyst_domain_count == 0
            and self.analyst_coverage_percentage
            is not None
            and not isclose(
                self.analyst_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_coverage_percentage must be zero "
                "when analyst_domain_count is zero."
            )

        if (
            self.analyst_resolved_count == 0
            and self.analyst_coverage_percentage
            is not None
            and not isclose(
                self.analyst_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_coverage_percentage must be zero "
                "when analyst_resolved_count is zero."
            )

        if (
            self.analyst_resolved_count is not None
            and self.analyst_resolved_count > 0
            and self.analyst_coverage_percentage is not None
            and isclose(
                self.analyst_coverage_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_coverage_percentage must be "
                "greater than zero when "
                "analyst_resolved_count is positive."
            )

        if (
            self.analyst_domain_count == 0
            and self.analyst_coverage_state is not None
            and self.analyst_coverage_state
            != "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_coverage_state must be "
                "UNAVAILABLE when analyst_domain_count "
                "is zero."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_domain_count > 0
            and self.analyst_coverage_state
            == "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_coverage_state cannot be "
                "UNAVAILABLE when analyst_domain_count "
                "is positive."
            )

        if (
            self.analyst_resolved_count == 0
            and self.analyst_coverage_state is not None
            and self.analyst_coverage_state
            not in {
                "UNAVAILABLE",
                "UNRESOLVED",
            }
        ):
            raise ValueError(
                "analyst_coverage_state must be "
                "UNAVAILABLE or UNRESOLVED when "
                "analyst_resolved_count is zero."
            )

        if (
            self.analyst_resolved_count is not None
            and self.analyst_resolved_count > 0
            and self.analyst_coverage_state is not None
            and self.analyst_coverage_state
            not in {
                "PARTIAL",
                "COMPLETE",
            }
        ):
            raise ValueError(
                "analyst_coverage_state must be "
                "PARTIAL or COMPLETE when "
                "analyst_resolved_count is positive."
            )

        if (
            self.analyst_enabled_unresolved_count == 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            not in {
                "UNAVAILABLE",
                "DISABLED",
                "OPERATIONAL",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNAVAILABLE, DISABLED, or OPERATIONAL "
                "when analyst_enabled_unresolved_count "
                "is zero."
            )

        if (
            self.analyst_enabled_unresolved_count
            is not None
            and self.analyst_enabled_unresolved_count > 0
            and self.analyst_operational_status
            is not None
            and self.analyst_operational_status
            not in {
                "UNRESOLVED",
                "DEGRADED",
            }
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNRESOLVED or DEGRADED when "
                "analyst_enabled_unresolved_count "
                "is positive."
            )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_unresolved_count
            is not None
            and self.analyst_operational_percentage
            is not None
        ):
            expected_operational_percentage = (
                (
                    (
                        self.analyst_enabled_count
                        - self.analyst_enabled_unresolved_count
                    )
                    / self.analyst_enabled_count
                )
                * 100.0
                if self.analyst_enabled_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_operational_percentage,
                expected_operational_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_operational_percentage must agree "
                    "with analyst_enabled_unresolved_count and "
                    "analyst_enabled_count."
                )

        if (
            self.analyst_enabled_unresolved_count == 0
            and self.analyst_operational_percentage
            is not None
            and not (
                isclose(
                    self.analyst_operational_percentage,
                    0.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
                or isclose(
                    self.analyst_operational_percentage,
                    100.0,
                    rel_tol=1e-9,
                    abs_tol=1e-6,
                )
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be "
                "zero or 100 when "
                "analyst_enabled_unresolved_count is zero."
            )

        if (
            self.analyst_enabled_unresolved_count
            is not None
            and self.analyst_enabled_unresolved_count > 0
            and self.analyst_operational_percentage
            is not None
            and isclose(
                self.analyst_operational_percentage,
                100.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be "
                "less than 100 when "
                "analyst_enabled_unresolved_count is positive."
            )

        if (
            self.analyst_operational_status is not None
            and self.analyst_enabled_count is not None
            and self.analyst_enabled_unresolved_count
            is not None
        ):
            if self.analyst_enabled_count == 0:
                expected_operational_statuses = {
                    "UNAVAILABLE",
                    "DISABLED",
                }

            elif (
                self.analyst_enabled_unresolved_count
                == self.analyst_enabled_count
            ):
                expected_operational_statuses = {
                    "UNRESOLVED",
                }

            elif (
                self.analyst_enabled_unresolved_count
                > 0
            ):
                expected_operational_statuses = {
                    "DEGRADED",
                }

            else:
                expected_operational_statuses = {
                    "OPERATIONAL",
                }

            if (
                self.analyst_operational_status
                not in expected_operational_statuses
            ):
                raise ValueError(
                    "analyst_operational_status must agree "
                    "with analyst_enabled_count and "
                    "analyst_enabled_unresolved_count."
                )

        if (
            self.analyst_enabled_resolved_count is not None
            and self.analyst_enabled_unresolved_count is not None
            and self.analyst_operational_percentage is not None
        ):
            enabled_component_count = (
                self.analyst_enabled_resolved_count
                + self.analyst_enabled_unresolved_count
            )

            expected_operational_percentage = (
                (
                    self.analyst_enabled_resolved_count
                    / enabled_component_count
                )
                * 100.0
                if enabled_component_count > 0
                else 0.0
            )

            if not isclose(
                self.analyst_operational_percentage,
                expected_operational_percentage,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    "analyst_operational_percentage must agree "
                    "with analyst_enabled_resolved_count and "
                    "analyst_enabled_unresolved_count."
                )

        if (
            self.analyst_operational_status is not None
            and self.analyst_enabled_resolved_count is not None
            and self.analyst_enabled_unresolved_count is not None
        ):
            if (
                self.analyst_enabled_resolved_count == 0
                and self.analyst_enabled_unresolved_count == 0
            ):
                expected_operational_statuses = {
                    "UNAVAILABLE",
                    "DISABLED",
                }

            elif self.analyst_enabled_resolved_count == 0:
                expected_operational_statuses = {
                    "UNRESOLVED",
                }

            elif self.analyst_enabled_unresolved_count > 0:
                expected_operational_statuses = {
                    "DEGRADED",
                }

            else:
                expected_operational_statuses = {
                    "OPERATIONAL",
                }

            if (
                self.analyst_operational_status
                not in expected_operational_statuses
            ):
                raise ValueError(
                    "analyst_operational_status must agree "
                    "with analyst_enabled_resolved_count and "
                    "analyst_enabled_unresolved_count."
                )

        if (
            self.analyst_enabled_count is not None
            and self.analyst_enabled_resolved_count is not None
            and self.analyst_enabled_unresolved_count is not None
            and self.analyst_enabled_count
            != (
                self.analyst_enabled_resolved_count
                + self.analyst_enabled_unresolved_count
            )
        ):
            raise ValueError(
                "analyst_enabled_count must equal "
                "analyst_enabled_resolved_count plus "
                "analyst_enabled_unresolved_count."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_enabled_resolved_count is not None
            and self.analyst_enabled_unresolved_count is not None
            and (
                self.analyst_enabled_resolved_count
                + self.analyst_enabled_unresolved_count
            )
            > self.analyst_domain_count
        ):
            raise ValueError(
                "analyst_enabled_resolved_count plus "
                "analyst_enabled_unresolved_count must not "
                "exceed analyst_domain_count."
            )

        if (
            self.analyst_operational_status is not None
            and self.analyst_domain_count is not None
            and self.analyst_enabled_resolved_count
            is not None
            and self.analyst_enabled_unresolved_count
            is not None
        ):
            if (
                self.analyst_enabled_resolved_count == 0
                and self.analyst_enabled_unresolved_count == 0
            ):
                expected_operational_status = (
                    "UNAVAILABLE"
                    if self.analyst_domain_count == 0
                    else "DISABLED"
                )

            elif self.analyst_enabled_resolved_count == 0:
                expected_operational_status = "UNRESOLVED"

            elif self.analyst_enabled_unresolved_count > 0:
                expected_operational_status = "DEGRADED"

            else:
                expected_operational_status = "OPERATIONAL"

            if (
                self.analyst_operational_status
                != expected_operational_status
            ):
                raise ValueError(
                    "analyst_operational_status must agree "
                    "with analyst_domain_count, "
                    "analyst_enabled_resolved_count, and "
                    "analyst_enabled_unresolved_count."
                )

        if (
            self.analyst_domain_count == 0
            and self.analyst_operational_percentage is not None
            and not isclose(
                self.analyst_operational_percentage,
                0.0,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                "analyst_operational_percentage must be zero "
                "when analyst_domain_count is zero."
            )

        if (
            self.analyst_domain_count == 0
            and self.analyst_operational_status is not None
            and self.analyst_operational_status != "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_operational_status must be "
                "UNAVAILABLE when analyst_domain_count is zero."
            )

        if (
            self.analyst_domain_count is not None
            and self.analyst_domain_count > 0
            and self.analyst_operational_status == "UNAVAILABLE"
        ):
            raise ValueError(
                "analyst_operational_status must not be "
                "UNAVAILABLE when analyst_domain_count is positive."
            )

        for field_name in (
            "decision_reasons",
            "decision_warnings",
            "trade_reasons",
            "trade_warnings",
            "market_phase_supporting_domains",
            "market_phase_opposing_domains",
            "institutional_bias_supporting_domains",
            "institutional_bias_opposing_domains",
            "acceptance_evidence",
            "acceptance_warnings",
            "trend_evidence",
            "trend_warnings",
        ):
            value = getattr(
                self,
                field_name,
            )

            normalized = (
                self._normalize_text_items(
                    field_name=field_name,
                    value=value,
                )
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        object.__setattr__(
            self,
            "analyst_summary",
            self._normalize_analyst_summary(
                self.analyst_summary
            ),
        )

        for field_name in (
            "latest_cycle_started_at",
            "latest_cycle_completed_at",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                self._validate_aware_datetime(
                    field_name=field_name,
                    value=value,
                )

        if (
            self.setup_lifecycle_confidence is not None
            and (
                isinstance(
                    self.setup_lifecycle_confidence,
                    bool,
                )
                or not isinstance(
                    self.setup_lifecycle_confidence,
                    int | float,
                )
            )
        ):
            raise TypeError(
                "setup_lifecycle_confidence must be a "
                "number or None."
            )

        if (
            self.setup_lifecycle_confidence is not None
            and not 0.0
            <= float(
                self.setup_lifecycle_confidence
            )
            <= 100.0
        ):
            raise ValueError(
                "setup_lifecycle_confidence must be "
                "between 0 and 100."
            )

        if (
            self.setup_lifecycle_atr_distance is not None
            and (
                isinstance(
                    self.setup_lifecycle_atr_distance,
                    bool,
                )
                or not isinstance(
                    self.setup_lifecycle_atr_distance,
                    int | float,
                )
            )
        ):
            raise TypeError(
                "setup_lifecycle_atr_distance must be "
                "a number or None."
            )

        if (
            self.setup_lifecycle_atr_distance is not None
            and self.setup_lifecycle_atr_distance < 0
        ):
            raise ValueError(
                "setup_lifecycle_atr_distance cannot "
                "be negative."
            )


        if (
            self.latest_cycle_started_at
            is not None
            and self.latest_cycle_completed_at
            is not None
            and self.latest_cycle_completed_at
            < self.latest_cycle_started_at
        ):
            raise ValueError(
                "latest_cycle_completed_at cannot be "
                "before latest_cycle_started_at."
            )

        if (
            self.analyst_confidence_coverage_state
            is not None
            and self.analyst_domain_count is not None
            and self.analyst_confidence_count is not None
        ):
            if self.analyst_domain_count == 0:
                expected_confidence_coverage_state = (
                    "UNAVAILABLE"
                )

            elif self.analyst_confidence_count == 0:
                expected_confidence_coverage_state = (
                    "MISSING"
                )

            elif (
                self.analyst_confidence_count
                < self.analyst_domain_count
            ):
                expected_confidence_coverage_state = (
                    "PARTIAL"
                )

            else:
                expected_confidence_coverage_state = (
                    "COMPLETE"
                )

            if (
                self.analyst_confidence_coverage_state
                != expected_confidence_coverage_state
            ):
                raise ValueError(
                    "analyst_confidence_coverage_state "
                    "must agree with analyst_domain_count "
                    "and analyst_confidence_count."
                )


        if (
            self.analyst_enabled_confidence_coverage_state
            is not None
            and self.analyst_domain_count is not None
            and self.analyst_enabled_count is not None
            and self.analyst_enabled_confidence_count
            is not None
        ):
            if self.analyst_domain_count == 0:
                expected_enabled_confidence_coverage_state = (
                    "UNAVAILABLE"
                )

            elif self.analyst_enabled_count == 0:
                expected_enabled_confidence_coverage_state = (
                    "DISABLED"
                )

            elif (
                self.analyst_enabled_confidence_count
                == 0
            ):
                expected_enabled_confidence_coverage_state = (
                    "MISSING"
                )

            elif (
                self.analyst_enabled_confidence_count
                < self.analyst_enabled_count
            ):
                expected_enabled_confidence_coverage_state = (
                    "PARTIAL"
                )

            else:
                expected_enabled_confidence_coverage_state = (
                    "COMPLETE"
                )

            if (
                self.analyst_enabled_confidence_coverage_state
                != expected_enabled_confidence_coverage_state
            ):
                raise ValueError(
                    "analyst_enabled_confidence_coverage_state "
                    "must agree with analyst_domain_count, "
                    "analyst_enabled_count, and "
                    "analyst_enabled_confidence_count."
                )

    @property
    def has_cycle(
        self,
    ) -> bool:
        return (
            self.latest_cycle_status
            is not None
        )

    @property
    def cycle_failed(
        self,
    ) -> bool:
        return (
            self.latest_cycle_status
            is AnalysisCycleStatus.FAILED
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        payload = self.health.to_dict()

        payload.update(
            {
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "latest_cycle_status": (
                    self.latest_cycle_status.value
                    if (
                        self.latest_cycle_status
                        is not None
                    )
                    else None
                ),
                "latest_cycle_message": (
                    self.latest_cycle_message
                ),
                "latest_cycle_started_at": (
                    self.latest_cycle_started_at
                    .isoformat()
                    if (
                        self.latest_cycle_started_at
                        is not None
                    )
                    else None
                ),
                "latest_cycle_completed_at": (
                    self.latest_cycle_completed_at
                    .isoformat()
                    if (
                        self.latest_cycle_completed_at
                        is not None
                    )
                    else None
                ),
                "market_session": (
                    self.market_session
                ),
                "latest_decision": (
                    self.latest_decision
                ),
                "decision_confidence": (
                    self.decision_confidence
                ),
                "decision_actionable": (
                    self.decision_actionable
                ),
                "decision_recommendation": (
                    self.decision_recommendation
                ),
                "decision_reasons": list(
                    self.decision_reasons
                ),
                "decision_warnings": list(
                    self.decision_warnings
                ),
                "analyst_summary": {
                    analyst_id: dict(details)
                    for analyst_id, details
                    in self.analyst_summary.items()
                },
                "trade_direction": (
                    self.trade_direction
                ),
                "trade_plan_valid": (
                    self.trade_plan_valid
                ),
                "trade_entry": (
                    self.trade_entry
                ),
                "trade_stop": (
                    self.trade_stop
                ),
                "trade_target1": (
                    self.trade_target1
                ),
                "trade_target2": (
                    self.trade_target2
                ),
                "trade_rr1": (
                    self.trade_rr1
                ),
                "trade_rr2": (
                    self.trade_rr2
                ),
                "trade_quality": (
                    self.trade_quality
                ),
                "trade_narrative": (
                    self.trade_narrative
                ),
                "trade_reasons": list(
                    self.trade_reasons
                ),
                "trade_warnings": list(
                    self.trade_warnings
                ),
                "position_size_quantity": (
                    self.position_size_quantity
                ),
                "position_size_notional": (
                    self.position_size_notional
                ),
                "position_size_risk_budget": (
                    self.position_size_risk_budget
                ),
                "position_size_actual_risk": (
                    self.position_size_actual_risk
                ),
                "position_size_actual_risk_percent": (
                    self.position_size_actual_risk_percent
                ),
                "position_size_risk_percent": (
                    self.position_size_risk_percent
                ),
                "position_size_actionable": (
                    self.position_size_actionable
                ),
                "position_size_warnings": list(
                    self.position_size_warnings
                ),
                "execution_candidate_strategy": (
                    self.execution_candidate_strategy
                ),
                "execution_candidate_direction": (
                    self.execution_candidate_direction
                ),
                "execution_candidate_quantity": (
                    self.execution_candidate_quantity
                ),
                "execution_candidate_entry": (
                    self.execution_candidate_entry
                ),
                "execution_candidate_stop": (
                    self.execution_candidate_stop
                ),
                "execution_candidate_target1": (
                    self.execution_candidate_target1
                ),
                "execution_candidate_target2": (
                    self.execution_candidate_target2
                ),
                "execution_candidate_notional": (
                    self.execution_candidate_notional
                ),
                "execution_candidate_risk_amount": (
                    self.execution_candidate_risk_amount
                ),
                "execution_candidate_valid": (
                    self.execution_candidate_valid
                ),
                "execution_candidate_actionable": (
                    self.execution_candidate_actionable
                ),
                "execution_candidate_warnings": list(
                    self.execution_candidate_warnings
                ),
                "execution_order_intent_side": (
                    self.execution_order_intent_side
                ),
                "execution_order_intent_quantity": (
                    self.execution_order_intent_quantity
                ),
                "execution_order_intent_order_type": (
                    self.execution_order_intent_order_type
                ),
                "execution_order_intent_entry_price": (
                    self.execution_order_intent_entry_price
                ),
                "execution_order_intent_stop_price": (
                    self.execution_order_intent_stop_price
                ),
                "execution_order_intent_target1_price": (
                    self.execution_order_intent_target1_price
                ),
                "execution_order_intent_target2_price": (
                    self.execution_order_intent_target2_price
                ),
                "execution_order_intent_time_in_force": (
                    self.execution_order_intent_time_in_force
                ),
                "execution_order_intent_valid": (
                    self.execution_order_intent_valid
                ),
                "execution_order_intent_actionable": (
                    self.execution_order_intent_actionable
                ),
                "execution_order_intent_warnings": list(
                    self.execution_order_intent_warnings
                ),
                "institutional_bias": (
                    self.institutional_bias
                ),
                "institutional_bias_confidence": (
                    self.institutional_bias_confidence
                ),
                "market_phase": (
                    self.market_phase
                ),
                "market_phase_confidence": (
                    self.market_phase_confidence
                ),
                "institutional_bias_strength": (
                    self.institutional_bias_strength
                ),
                "institutional_bias_bullish_score": (
                    self.institutional_bias_bullish_score
                ),
                "institutional_bias_bearish_score": (
                    self.institutional_bias_bearish_score
                ),
                "institutional_bias_agreement_count": (
                    self.institutional_bias_agreement_count
                ),
                "institutional_bias_conflict_count": (
                    self.institutional_bias_conflict_count
                ),
                "institutional_bias_supporting_domains": list(
                    self.institutional_bias_supporting_domains
                ),
                "institutional_bias_opposing_domains": list(
                    self.institutional_bias_opposing_domains
                ),
                "confluence_direction": (
                    self.confluence_direction
                ),
                "confluence_score": (
                    self.confluence_score
                ),
                "confluence_agreement_count": (
                    self.confluence_agreement_count
                ),
                "confluence_conflict_count": (
                    self.confluence_conflict_count
                ),
                "confluence_confidence_adjustment": (
                    self.confluence_confidence_adjustment
                ),
                "confluence_structure_support": (
                    self.confluence_structure_support
                ),
                "confluence_liquidity_support": (
                    self.confluence_liquidity_support
                ),
                "confluence_order_block_support": (
                    self.confluence_order_block_support
                ),
                "confluence_auction_support": (
                    self.confluence_auction_support
                ),
                "confluence_pressure_support": (
                    self.confluence_pressure_support
                ),
                "confluence_participation_support": (
                    self.confluence_participation_support
                ),
                "confluence_value_support": (
                    self.confluence_value_support
                ),
                "confluence_bullish_count": (
                    self.confluence_bullish_count
                ),
                "confluence_bearish_count": (
                    self.confluence_bearish_count
                ),
                "confluence_neutral_count": (
                    self.confluence_neutral_count
                ),
                "confluence_unknown_count": (
                    self.confluence_unknown_count
                ),
                "confluence_domain_count": (
                    self.confluence_domain_count
                ),
                "market_phase_strength": (
                    self.market_phase_strength
                ),
                "market_phase_agreement_count": (
                    self.market_phase_agreement_count
                ),
                "market_phase_conflict_count": (
                    self.market_phase_conflict_count
                ),
                "market_phase_supporting_domains": list(
                    self.market_phase_supporting_domains
                ),
                "market_phase_opposing_domains": list(
                    self.market_phase_opposing_domains
                ),
                "setup_lifecycle_state": (
                    self.setup_lifecycle_state
                ),
                "setup_lifecycle_direction": (
                    self.setup_lifecycle_direction
                ),
                "setup_lifecycle_confidence": (
                    self.setup_lifecycle_confidence
                ),
                "setup_lifecycle_atr_distance": (
                    self.setup_lifecycle_atr_distance
                ),
                "setup_lifecycle_action": (
                    self.setup_lifecycle_action
                ),
                "setup_lifecycle_reason": (
                    self.setup_lifecycle_reason
                ),
                "latest_error_type": (
                    self.latest_error_type
                ),
                "has_cycle": self.has_cycle,
                "cycle_failed": (
                    self.cycle_failed
                ),
                "acceptance_confirmed": (
                    self.acceptance_confirmed
                ),
                "acceptance_direction": (
                    self.acceptance_direction
                ),
                "acceptance_level": (
                    self.acceptance_level
                ),
                "acceptance_score": (
                    self.acceptance_score
                ),
                "acceptance_confidence": (
                    self.acceptance_confidence
                ),
                "acceptance_trigger_price": (
                    self.acceptance_trigger_price
                ),
                "acceptance_previous_level": (
                    self.acceptance_previous_level
                ),
                "acceptance_pullback_low": (
                    self.acceptance_pullback_low
                ),
                "acceptance_pullback_high": (
                    self.acceptance_pullback_high
                ),
                "acceptance_reason": (
                    self.acceptance_reason
                ),
                "acceptance_evidence": list(
                    self.acceptance_evidence
                ),
                "acceptance_warnings": list(
                    self.acceptance_warnings
                ),
                "trend_analyst": (
                    self.trend_analyst
                ),
                "trend_opinion": (
                    self.trend_opinion
                ),
                "trend_confidence": (
                    self.trend_confidence
                ),
                "trend_enabled": (
                    self.trend_enabled
                ),
                "trend_evidence": list(
                    self.trend_evidence
                ),
                "trend_warnings": list(
                    self.trend_warnings
                ),
                "structure_analyst": (
                    self.structure_analyst
                ),
                "structure_opinion": (
                    self.structure_opinion
                ),
                "structure_confidence": (
                    self.structure_confidence
                ),
                "structure_enabled": (
                    self.structure_enabled
                ),
                "liquidity_analyst": (
                    self.liquidity_analyst
                ),
                "liquidity_opinion": (
                    self.liquidity_opinion
                ),
                "liquidity_confidence": (
                    self.liquidity_confidence
                ),
                "liquidity_enabled": (
                    self.liquidity_enabled
                ),
                "order_block_analyst": (
                    self.order_block_analyst
                ),
                "order_block_opinion": (
                    self.order_block_opinion
                ),
                "order_block_confidence": (
                    self.order_block_confidence
                ),
                "order_block_enabled": (
                    self.order_block_enabled
                ),
                "auction_analyst": (
                    self.auction_analyst
                ),
                "auction_opinion": (
                    self.auction_opinion
                ),
                "auction_confidence": (
                    self.auction_confidence
                ),
                "auction_enabled": (
                    self.auction_enabled
                ),
                "pressure_analyst": (
                    self.pressure_analyst
                ),
                "pressure_opinion": (
                    self.pressure_opinion
                ),
                "pressure_confidence": (
                    self.pressure_confidence
                ),
                "pressure_enabled": (
                    self.pressure_enabled
                ),
                "participation_analyst": (
                    self.participation_analyst
                ),
                "participation_opinion": (
                    self.participation_opinion
                ),
                "participation_confidence": (
                    self.participation_confidence
                ),
                "participation_enabled": (
                    self.participation_enabled
                ),
                "value_analyst": (
                    self.value_analyst
                ),
                "value_opinion": (
                    self.value_opinion
                ),
                "value_confidence": (
                    self.value_confidence
                ),
                "value_enabled": (
                    self.value_enabled
                ),
                "analyst_domain_count": (
                    self.analyst_domain_count
                ),
                "analyst_enabled_count": (
                    self.analyst_enabled_count
                ),
                "analyst_resolved_count": (
                    self.analyst_resolved_count
                ),
                "analyst_enabled_resolved_count": (
                    self.analyst_enabled_resolved_count
                ),
                "analyst_enabled_unresolved_count": (
                    self.analyst_enabled_unresolved_count
                ),
                "analyst_confidence_count": (
                    self.analyst_confidence_count
                ),
                "analyst_enabled_confidence_count": (
                    self.analyst_enabled_confidence_count
                ),
                "analyst_missing_confidence_count": (
                    self.analyst_missing_confidence_count
                ),
                "analyst_enabled_missing_confidence_count": (
                    self.analyst_enabled_missing_confidence_count
                ),
                "analyst_average_confidence": (
                    self.analyst_average_confidence
                ),
                "analyst_enabled_average_confidence": (
                    self.analyst_enabled_average_confidence
                ),
                "analyst_confidence_coverage_percentage": (
                    self.analyst_confidence_coverage_percentage
                ),
                "analyst_enabled_confidence_coverage_percentage": (
                    self.analyst_enabled_confidence_coverage_percentage
                ),
                "analyst_confidence_coverage_state": (
                    self.analyst_confidence_coverage_state
                ),
                "analyst_confidence_coverage_message": (
                    self.analyst_confidence_coverage_message
                ),
                "analyst_enabled_confidence_coverage_state": (
                    self.analyst_enabled_confidence_coverage_state
                ),
                "analyst_enabled_confidence_coverage_message": (
                    self.analyst_enabled_confidence_coverage_message
                ),
                "analyst_coverage_percentage": (
                    self.analyst_coverage_percentage
                ),
                "analyst_coverage_state": (
                    self.analyst_coverage_state
                ),
                "analyst_coverage_message": (
                    self.analyst_coverage_message
                ),
                "analyst_operational_status": (
                    self.analyst_operational_status
                ),
                "analyst_operational_message": (
                    self.analyst_operational_message
                ),
                "analyst_operational_percentage": (
                    self.analyst_operational_percentage
                ),
                "broker_submission_broker": (
                    self.broker_submission_broker
                ),
                "broker_submission_symbol": (
                    self.broker_submission_symbol
                ),
                "broker_submission_side": (
                    self.broker_submission_side
                ),
                "broker_submission_quantity": (
                    self.broker_submission_quantity
                ),
                "broker_submission_accepted": (
                    self.broker_submission_accepted
                ),
                "broker_submission_order_id": (
                    self.broker_submission_order_id
                ),
                "broker_submission_status": (
                    self.broker_submission_status
                ),
                "broker_submission_message": (
                    self.broker_submission_message
                ),
                "broker_submission_warnings": list(
                    self.broker_submission_warnings
                ),
                "execution_safety_state": self.execution_safety_state,
                "execution_safety_symbol": self.execution_safety_symbol,
                "execution_safety_order_notional": (
                    self.execution_safety_order_notional
                ),
                "execution_safety_risk_amount": self.execution_safety_risk_amount,
                "execution_safety_maximum_order_notional": (
                    self.execution_safety_maximum_order_notional
                ),
                "execution_safety_maximum_risk_amount": (
                    self.execution_safety_maximum_risk_amount
                ),
                "execution_safety_allowed": self.execution_safety_allowed,
                "execution_safety_kill_switch_active": (
                    self.execution_safety_kill_switch_active
                ),
                "execution_safety_violations": list(
                    self.execution_safety_violations
                ),
                "execution_safety_warnings": list(
                    self.execution_safety_warnings
                ),
                "execution_submission_fingerprint": (
                    self.execution_submission_fingerprint
                ),
                "execution_submission_reserved_at": (
                    self.execution_submission_reserved_at
                ),
                "concurrent_position_broker": self.concurrent_position_broker,
                "concurrent_position_open_count": (
                    self.concurrent_position_open_count
                ),
                "concurrent_position_maximum": self.concurrent_position_maximum,
                "concurrent_position_symbol_already_open": (
                    self.concurrent_position_symbol_already_open
                ),
                "concurrent_position_allowed": self.concurrent_position_allowed,
                "concurrent_position_exposure_age_seconds": (
                    self.concurrent_position_exposure_age_seconds
                ),
                "concurrent_position_maximum_exposure_age_seconds": (
                    self.concurrent_position_maximum_exposure_age_seconds
                ),
                "concurrent_position_exposure_fresh": (
                    self.concurrent_position_exposure_fresh
                ),
                "concurrent_position_violations": list(
                    self.concurrent_position_violations
                ),
                "daily_loss_broker": self.daily_loss_broker,
                "daily_loss_realized_pnl": self.daily_loss_realized_pnl,
                "daily_loss_unrealized_pnl": self.daily_loss_unrealized_pnl,
                "daily_loss_total_pnl": self.daily_loss_total_pnl,
                "daily_loss_amount": self.daily_loss_amount,
                "daily_loss_maximum": self.daily_loss_maximum,
                "daily_loss_within_limit": self.daily_loss_within_limit,
                "daily_loss_allowed": self.daily_loss_allowed,
                "daily_loss_violations": list(self.daily_loss_violations),
                "protected_submission_broker": self.protected_submission_broker,
                "protected_submission_quantity": self.protected_submission_quantity,
                "protected_submission_accepted": self.protected_submission_accepted,
                "protected_submission_status": self.protected_submission_status,
                "protected_submission_message": self.protected_submission_message,
                "protected_submission_order_count": self.protected_submission_order_count,
                "protected_submission_rollback_attempted": (
                    self.protected_submission_rollback_attempted
                ),
                "protected_submission_rollback_succeeded": (
                    self.protected_submission_rollback_succeeded
                ),
                "protected_submission_orders": list(
                    self.protected_submission_orders
                ),
                "protected_submission_warnings": list(
                    self.protected_submission_warnings
                ),
            }
        )

        return payload

    def to_json(
        self,
        *,
        indent: int | None = None,
    ) -> str:
        if (
            indent is not None
            and (
                isinstance(
                    indent,
                    bool,
                )
                or not isinstance(
                    indent,
                    int,
                )
            )
        ):
            raise TypeError(
                "indent must be an int or None."
            )

        if (
            indent is not None
            and indent < 0
        ):
            raise ValueError(
                "indent cannot be negative."
            )

        if indent is None:
            return json.dumps(
                self.to_dict(),
                separators=(
                    ",",
                    ":",
                ),
                sort_keys=True,
                allow_nan=False,
            )

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
            allow_nan=False,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        field_name: str,
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        *,
        field_name: str,
        value: object,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string or None."
            )

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _normalize_text_items(
        *,
        field_name: str,
        value: object,
    ) -> tuple[str, ...]:
        if not isinstance(
            value,
            tuple | list,
        ):
            raise TypeError(
                f"{field_name} must be a tuple "
                "or list of strings."
            )

        normalized_items: list[str] = []

        for item in value:
            if not isinstance(
                item,
                str,
            ):
                raise TypeError(
                    f"{field_name} must contain "
                    "only strings."
                )

            normalized = item.strip()

            if normalized:
                normalized_items.append(
                    normalized
                )

        return tuple(
            normalized_items
        )

    @staticmethod
    def _validate_aware_datetime(
        *,
        field_name: str,
        value: object,
    ) -> None:
        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _normalize_analyst_summary(
        summary: object,
    ) -> dict[str, dict[str, object]]:
        if not isinstance(summary, dict):
            raise TypeError(
                "analyst_summary must be a dictionary"
            )

        normalized: dict[
            str,
            dict[str, object],
        ] = {}

        for analyst_id, details in summary.items():
            if not isinstance(analyst_id, str):
                raise TypeError(
                    "analyst_summary keys must be strings"
                )

            normalized_id = (
                analyst_id.strip().upper()
            )

            if not normalized_id:
                continue

            if not isinstance(details, dict):
                raise TypeError(
                    "analyst_summary values must be "
                    "dictionaries"
                )

            opinion = details.get(
                "opinion",
                "",
            )

            if not isinstance(opinion, str):
                raise TypeError(
                    "analyst_summary opinion must be "
                    "a string"
                )

            confidence = details.get(
                "confidence",
                0.0,
            )

            if (
                isinstance(confidence, bool)
                or not isinstance(
                    confidence,
                    int | float,
                )
            ):
                raise TypeError(
                    "analyst_summary confidence must "
                    "be numeric"
                )

            confidence_value = float(
                confidence
            )

            if not (
                0.0
                <= confidence_value
                <= 100.0
            ):
                raise ValueError(
                    "analyst_summary confidence must "
                    "be between 0 and 100"
                )

            enabled = details.get(
                "enabled",
                True,
            )

            if not isinstance(enabled, bool):
                raise TypeError(
                    "analyst_summary enabled must be "
                    "a boolean"
                )

            normalized[normalized_id] = {
                "opinion": opinion.strip(),
                "confidence": confidence_value,
                "enabled": enabled,
            }

        return normalized
