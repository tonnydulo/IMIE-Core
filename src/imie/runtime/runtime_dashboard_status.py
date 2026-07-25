from __future__ import annotations

import json

from dataclasses import dataclass
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

        for field_name in (
            "trade_entry",
            "trade_stop",
            "trade_target1",
            "trade_target2",
            "trade_rr1",
            "trade_rr2",
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
            "trade_reasons",
            "trade_warnings",
            "market_phase_supporting_domains",
            "market_phase_opposing_domains",
            "institutional_bias_supporting_domains",
            "institutional_bias_opposing_domains",
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