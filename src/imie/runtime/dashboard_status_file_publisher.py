from __future__ import annotations

import os

from enum import Enum

from pathlib import Path
from threading import RLock

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.runtime_dashboard_status import (
    RuntimeDashboardStatus,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)


class DashboardStatusFilePublisher:
    """
    Maintains the latest unified runtime-dashboard payload.

    The publisher accepts both RuntimeHealthSummary and
    AnalysisCycleResult instances. Each accepted update rewrites
    the dashboard file atomically when a health summary is
    available.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        symbol: str,
        timeframe: str,
        indent: int | None = 2,
        create_parent_directories: bool = True,
    ) -> None:
        if not isinstance(
            path,
            str | Path,
        ):
            raise TypeError(
                "path must be a string or Path."
            )

        resolved_path = Path(
            path
        )

        if not str(
            resolved_path
        ).strip():
            raise ValueError(
                "path cannot be empty."
            )

        self._symbol = self._normalize_required_text(
            field_name="symbol",
            value=symbol,
        ).upper()

        self._timeframe = self._normalize_required_text(
            field_name="timeframe",
            value=timeframe,
        ).lower()

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

        if not isinstance(
            create_parent_directories,
            bool,
        ):
            raise TypeError(
                "create_parent_directories must be a bool."
            )

        self.path = resolved_path
        self.indent = indent
        self.create_parent_directories = (
            create_parent_directories
        )

        self._health: RuntimeHealthSummary | None = None
        self._latest_cycle: AnalysisCycleResult | None = None

        self._market_session: str | None = None
        self._latest_decision: str | None = None

        self._lock = RLock()

    @property
    def health(
        self,
    ) -> RuntimeHealthSummary | None:
        return self._health

    @property
    def latest_cycle(
        self,
    ) -> AnalysisCycleResult | None:
        return self._latest_cycle

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publish_result(
            result
        )


    def publish(
        self,
        value: (
            RuntimeHealthSummary
            | AnalysisCycleResult
        ),
    ) -> None:
        if isinstance(
            value,
            RuntimeHealthSummary,
        ):
            self.publish_health(
                value
            )

            return

        if isinstance(
            value,
            AnalysisCycleResult,
        ):
            self.publish_result(
                value
            )

            return

        raise TypeError(
            "value must be a RuntimeHealthSummary "
            "or AnalysisCycleResult."
        )

    def publish_health(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        if not isinstance(
            summary,
            RuntimeHealthSummary,
        ):
            raise TypeError(
                "summary must be a RuntimeHealthSummary."
            )

        with self._lock:
            self._health = summary
            self._write_if_ready()

    def publish_result(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
            )

        with self._lock:
            self._latest_cycle = result

            market_session = (
                self._market_session_from_result(
                    result
                )
            )

            if market_session is not None:
                self._market_session = (
                    market_session
                )

            latest_decision = (
                self._decision_from_result(
                    result
                )
            )

            if latest_decision is not None:
                self._latest_decision = (
                    latest_decision
                )

            self._write_if_ready()

    def update_market_session(
        self,
        market_session: str | None,
    ) -> None:
        normalized = self._normalize_optional_text(
            field_name="market_session",
            value=market_session,
        )

        with self._lock:
            self._market_session = normalized
            self._write_if_ready()

    def update_latest_decision(
        self,
        latest_decision: str | None,
    ) -> None:
        normalized = self._normalize_optional_text(
            field_name="latest_decision",
            value=latest_decision,
        )

        with self._lock:
            self._latest_decision = normalized
            self._write_if_ready()

    def build_status(
        self,
    ) -> RuntimeDashboardStatus:
        if self._health is None:
            raise RuntimeError(
                "A health summary is required before "
                "dashboard status can be built."
            )

        cycle = self._latest_cycle

        decision_result = (
            cycle.decision
            if cycle is not None
            else None
        )

        trade_plan = (
            decision_result.trade_plan
            if decision_result is not None
            else None
        )

        institutional_context = (
            decision_result.institutional_context
            if decision_result is not None
            else None
        )

        institutional_bias = (
            institutional_context.institutional_bias
            if institutional_context is not None
            else None
        )

        market_phase = (
            institutional_context.market_phase
            if institutional_context is not None
            else None
        )

        institutional_confluence = (
            institutional_context.institutional_confluence
            if institutional_context is not None
            else None
        )

        setup_lifecycle = (
            institutional_context.setup_lifecycle
            if institutional_context is not None
            else None
        )

        acceptance = (
            institutional_context.acceptance
            if institutional_context is not None
            else None
        )

        trend = (
            institutional_context.trend
            if institutional_context is not None
            else None
        )

        return RuntimeDashboardStatus(
            health=self._health,
            symbol=(
                cycle.symbol
                if cycle is not None
                else self._symbol
            ),
            timeframe=(
                cycle.timeframe
                if cycle is not None
                else self._timeframe
            ),
            latest_cycle_status=(
                cycle.status
                if cycle is not None
                else None
            ),
            latest_cycle_message=(
                cycle.message
                if cycle is not None
                else None
            ),
            latest_cycle_started_at=(
                cycle.started_at
                if cycle is not None
                else None
            ),
            latest_cycle_completed_at=(
                cycle.completed_at
                if cycle is not None
                else None
            ),
            market_session=self._market_session,
            latest_decision=self._latest_decision,
            decision_confidence=(
                float(
                    decision_result.confidence
                )
                if decision_result is not None
                else None
            ),
            decision_actionable=(
                decision_result.actionable
                if decision_result is not None
                else None
            ),
            decision_recommendation=(
                decision_result.recommendation
                if decision_result is not None
                else None
            ),
            decision_reasons=(
                tuple(
                    decision_result.reasons
                )
                if decision_result is not None
                else ()
            ),
            decision_warnings=(
                tuple(
                    decision_result.warnings
                )
                if decision_result is not None
                else ()
            ),
            analyst_summary=(
                {
                    analyst_id: dict(details)
                    for analyst_id, details
                    in decision_result.analyst_summary.items()
                }
                if decision_result is not None
                else {}
            ),
            trade_direction=(
                self._display_value(
                    trade_plan.direction
                )
                if trade_plan is not None
                else None
            ),

            trade_plan_valid=(
                trade_plan.valid
                if trade_plan is not None
                else None
            ),
            trade_entry=(
                trade_plan.entry
                if trade_plan is not None
                else None
            ),
            trade_stop=(
                trade_plan.stop
                if trade_plan is not None
                else None
            ),
            trade_target1=(
                trade_plan.target1
                if trade_plan is not None
                else None
            ),
            trade_target2=(
                trade_plan.target2
                if trade_plan is not None
                else None
            ),
            trade_rr1=(
                trade_plan.rr1
                if trade_plan is not None
                else None
            ),
            trade_rr2=(
                trade_plan.rr2
                if trade_plan is not None
                else None
            ),
            trade_quality=(
                trade_plan.quality
                if trade_plan is not None
                else None
            ),

            trade_narrative=(
                trade_plan.narrative
                if trade_plan is not None
                else None
            ),
            trade_reasons=(
                tuple(
                    trade_plan.reasons
                )
                if trade_plan is not None
                else ()
            ),
            trade_warnings=(
                tuple(
                    trade_plan.warnings
                )
                if trade_plan is not None
                else ()
            ),

            institutional_bias=(
                institutional_bias.direction.value
                if institutional_bias is not None
                else None
            ),
            institutional_bias_confidence=(
                institutional_bias.confidence
                if institutional_bias is not None
                else None
            ),
            institutional_bias_strength=(
                institutional_bias.strength
                if institutional_bias is not None
                else None
            ),
            institutional_bias_bullish_score=(
                institutional_bias.bullish_score
                if institutional_bias is not None
                else None
            ),
            institutional_bias_bearish_score=(
                institutional_bias.bearish_score
                if institutional_bias is not None
                else None
            ),
            institutional_bias_agreement_count=(
                institutional_bias.agreement_count
                if institutional_bias is not None
                else None
            ),
            institutional_bias_conflict_count=(
                institutional_bias.conflict_count
                if institutional_bias is not None
                else None
            ),
            institutional_bias_supporting_domains=(
                tuple(
                    institutional_bias.supporting_domains
                )
                if institutional_bias is not None
                else ()
            ),
            institutional_bias_opposing_domains=(
                tuple(
                    institutional_bias.opposing_domains
                )
                if institutional_bias is not None
                else ()
            ),
            market_phase=(
                market_phase.phase.value
                if market_phase is not None
                else None
            ),
            market_phase_confidence=(
                market_phase.confidence
                if market_phase is not None
                else None
            ),
            confluence_direction=(
                institutional_confluence
                .dominant_direction
                .value
                if institutional_confluence is not None
                else None
            ),
            confluence_score=(
                institutional_confluence.score
                if institutional_confluence is not None
                else None
            ),
            confluence_agreement_count=(
                institutional_confluence.agreement_count
                if institutional_confluence is not None
                else None
            ),
            confluence_conflict_count=(
                institutional_confluence.conflict_count
                if institutional_confluence is not None
                else None
            ),
            confluence_confidence_adjustment=(
                institutional_confluence.confidence_adjustment
                if institutional_confluence is not None
                else None
            ),
            confluence_structure_support=(
                institutional_confluence.structure_support
                if institutional_confluence is not None
                else None
            ),
            confluence_liquidity_support=(
                institutional_confluence.liquidity_support
                if institutional_confluence is not None
                else None
            ),
            confluence_order_block_support=(
                institutional_confluence.order_block_support
                if institutional_confluence is not None
                else None
            ),
            confluence_auction_support=(
                institutional_confluence.auction_support
                if institutional_confluence is not None
                else None
            ),
            confluence_pressure_support=(
                institutional_confluence.pressure_support
                if institutional_confluence is not None
                else None
            ),
            confluence_participation_support=(
                institutional_confluence.participation_support
                if institutional_confluence is not None
                else None
            ),
            confluence_value_support=(
                institutional_confluence.value_support
                if institutional_confluence is not None
                else None
            ),
            confluence_bullish_count=(
                institutional_confluence.bullish_count
                if institutional_confluence is not None
                else None
            ),
            confluence_bearish_count=(
                institutional_confluence.bearish_count
                if institutional_confluence is not None
                else None
            ),
            confluence_neutral_count=(
                institutional_confluence.neutral_count
                if institutional_confluence is not None
                else None
            ),
            confluence_unknown_count=(
                institutional_confluence.unknown_count
                if institutional_confluence is not None
                else None
            ),
            confluence_domain_count=(
                institutional_confluence.domain_count
                if institutional_confluence is not None
                else None
            ),
            market_phase_strength=(
                market_phase.strength
                if market_phase is not None
                else None
            ),
            market_phase_agreement_count=(
                market_phase.agreement_count
                if market_phase is not None
                else None
            ),
            market_phase_conflict_count=(
                market_phase.conflict_count
                if market_phase is not None
                else None
            ),
            market_phase_supporting_domains=(
                tuple(
                    market_phase.supporting_domains
                )
                if market_phase is not None
                else ()
            ),
            market_phase_opposing_domains=(
                tuple(
                    market_phase.opposing_domains
                )
                if market_phase is not None
                else ()
            ),

            setup_lifecycle_state=(
                setup_lifecycle.state
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_direction=(
                setup_lifecycle.direction
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_confidence=(
                setup_lifecycle.confidence
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_atr_distance=(
                setup_lifecycle.atr_distance
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_action=(
                setup_lifecycle.action
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_reason=(
                setup_lifecycle.reason
                if setup_lifecycle is not None
                else None
            ),
            acceptance_confirmed=(
                acceptance.accepted
                if acceptance is not None
                else None
            ),
            acceptance_direction=(
                acceptance.direction
                if acceptance is not None
                else None
            ),
            acceptance_level=(
                acceptance.level
                if acceptance is not None
                else None
            ),
            acceptance_score=(
                acceptance.score
                if acceptance is not None
                else None
            ),
            acceptance_confidence=(
                acceptance.confidence
                if acceptance is not None
                else None
            ),
            acceptance_trigger_price=(
                acceptance.trigger_price
                if acceptance is not None
                else None
            ),
            acceptance_previous_level=(
                acceptance.previous_level
                if acceptance is not None
                else None
            ),
            acceptance_pullback_low=(
                acceptance.pullback_low
                if acceptance is not None
                else None
            ),
            acceptance_pullback_high=(
                acceptance.pullback_high
                if acceptance is not None
                else None
            ),
            acceptance_reason=(
                acceptance.reason
                if acceptance is not None
                else None
            ),
            acceptance_evidence=(
                tuple(
                    acceptance.evidence
                )
                if acceptance is not None
                else ()
            ),
            acceptance_warnings=(
                tuple(
                    acceptance.warnings
                )
                if acceptance is not None
                else ()
            ),

            trend_analyst=(
                trend.analyst
                if trend is not None
                else None
            ),
            trend_opinion=(
                trend.opinion
                if trend is not None
                else None
            ),
            trend_confidence=(
                trend.confidence
                if trend is not None
                else None
            ),
            trend_enabled=(
                trend.enabled
                if trend is not None
                else None
            ),
            trend_evidence=(
                tuple(
                    trend.evidence
                )
                if trend is not None
                else ()
            ),
            trend_warnings=(
                tuple(
                    trend.warnings
                )
                if trend is not None
                else ()
            ),

            latest_error_type=(
                cycle.error_type
                if cycle is not None
                else None
            ),
        )
    

    def _write_if_ready(
        self,
    ) -> None:
        if self._health is None:
            return

        if self.create_parent_directories:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        status = self.build_status()

        payload = status.to_json(
            indent=self.indent
        )

        temporary_path = self.path.with_name(
            f".{self.path.name}.tmp"
        )

        try:
            temporary_path.write_text(
                payload + "\n",
                encoding="utf-8",
            )

            os.replace(
                temporary_path,
                self.path,
            )
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

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
    def _display_value(
        value: object | None,
    ) -> str | None:
        if value is None:
            return None

        if isinstance(
            value,
            Enum,
        ):
            enum_value = value.value

            if isinstance(
                enum_value,
                str,
            ):
                normalized = (
                    enum_value.strip()
                )

                return (
                    normalized
                    or None
                )

            return str(
                enum_value
            )

        normalized = str(
            value
        ).strip()

        return (
            normalized
            or None
        )

    @classmethod
    def _market_session_from_result(
        cls,
        result: AnalysisCycleResult,
    ) -> str | None:
        market_session = (
            result.market_session
        )

        if market_session is None:
            return None

        return cls._display_value(
            market_session.state
        )

    @classmethod
    def _decision_from_result(
        cls,
        result: AnalysisCycleResult,
    ) -> str | None:
        decision_result = (
            result.decision
        )

        if decision_result is None:
            return None

        return cls._display_value(
            decision_result.decision
        )