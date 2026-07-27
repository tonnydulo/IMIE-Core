from __future__ import annotations

import json

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

            normalized = float(
                value
            )

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
            "structure_analyst",
            "structure_opinion",
            "liquidity_analyst",
            "liquidity_opinion",
            "order_block_analyst",
            "order_block_opinion",
            "auction_analyst",
            "auction_opinion",
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
            )

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
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