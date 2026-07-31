import json

import math

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from imie.runtime import (
    AnalysisCycleStatus,
    RuntimeDashboardStatus,
    RuntimeHealthState,
    RuntimeHealthSummary,
)


NOW = datetime(
    2026,
    7,
    23,
    15,
    0,
    tzinfo=timezone.utc,
)


def make_health() -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=RuntimeHealthState.RUNNING,
        started_at=NOW,
        checked_at=(
            NOW
            + timedelta(
                minutes=5,
            )
        ),
        uptime_seconds=300.0,
        last_transition_at=NOW,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=2,
        error_type=None,
    )


def make_status(
    *,
    decision_confidence: float | None = None,
    decision_actionable: bool | None = None,
    decision_recommendation: str | None = None,
    decision_reasons: tuple[str, ...] = (),
    decision_warnings: tuple[str, ...] = (),
    analyst_summary: dict[str, dict[str, object]] | None = None,
    trade_direction: str | None = None,
    trade_narrative: str | None = None,
    trade_reasons: tuple[str, ...] = (),
    trade_warnings: tuple[str, ...] = (),

    institutional_bias: str | None = None,
    institutional_bias_confidence: float | None = None,
    institutional_bias_strength: float | None = None,
    institutional_bias_bullish_score: float | None = None,
    institutional_bias_bearish_score: float | None = None,
    institutional_bias_agreement_count: int | None = None,
    institutional_bias_conflict_count: int | None = None,
    institutional_bias_supporting_domains: tuple[str, ...] = (),
    institutional_bias_opposing_domains: tuple[str, ...] = (),


    confluence_direction: str | None = None,
    confluence_score: float | None = None,
    confluence_agreement_count: int | None = None,
    confluence_conflict_count: int | None = None,
    confluence_confidence_adjustment: float | None = None,
    confluence_structure_support: bool | None = None,
    confluence_liquidity_support: bool | None = None,
    confluence_order_block_support: bool | None = None,
    confluence_auction_support: bool | None = None,
    confluence_pressure_support: bool | None = None,
    confluence_participation_support: bool | None = None,
    confluence_value_support: bool | None = None,
    confluence_bullish_count: int | None = None,
    confluence_bearish_count: int | None = None,
    confluence_neutral_count: int | None = None,
    confluence_unknown_count: int | None = None,
    confluence_domain_count: int | None = None,

    market_phase: str | None = None,
    market_phase_confidence: float | None = None,
    market_phase_strength: float | None = None,
    market_phase_agreement_count: int | None = None,
    market_phase_conflict_count: int | None = None,
    market_phase_supporting_domains: tuple[str, ...] = (),
    market_phase_opposing_domains: tuple[str, ...] = (),

    setup_lifecycle_state: str | None = None,
    setup_lifecycle_direction: str | None = None,
    setup_lifecycle_confidence: float | None = None,
    setup_lifecycle_atr_distance: float | None = None,
    setup_lifecycle_action: str | None = None,
    setup_lifecycle_reason: str | None = None,

    acceptance_confidence: float | None = None,

    trend_analyst: str | None = None,
    trend_opinion: str | None = None,
    trend_confidence: float | None = None,
    trend_enabled: bool | None = None,
    trend_evidence: tuple[str, ...] = (),
    trend_warnings: tuple[str, ...] = (),

    structure_analyst: str | None = None,
    structure_opinion: str | None = None,
    structure_confidence: float | None = None,
    structure_enabled: bool | None = None,

    liquidity_analyst: str | None = None,
    liquidity_opinion: str | None = None,
    liquidity_confidence: float | None = None,
    liquidity_enabled: bool | None = None,

    order_block_analyst: str | None = None,
    order_block_opinion: str | None = None,
    order_block_confidence: float | None = None,
    order_block_enabled: bool | None = None,

    auction_analyst: str | None = None,
    auction_opinion: str | None = None,
    auction_confidence: float | None = None,
    auction_enabled: bool | None = None,

    pressure_analyst: str | None = None,
    pressure_opinion: str | None = None,
    pressure_confidence: float | None = None,
    pressure_enabled: bool | None = None,

    participation_analyst: str | None = None,
    participation_opinion: str | None = None,
    participation_confidence: float | None = None,
    participation_enabled: bool | None = None,

    value_analyst: str | None = None,
    value_opinion: str | None = None,
    value_confidence: float | None = None,
    value_enabled: bool | None = None,

    analyst_domain_count: int | None = None,
    analyst_enabled_count: int | None = None,
    analyst_resolved_count: int | None = None,
    analyst_enabled_resolved_count: int | None = None,
    analyst_enabled_unresolved_count: int | None = None,
    analyst_average_confidence: float | None = None,
    analyst_enabled_average_confidence: float | None = None,
    analyst_coverage_percentage: float | None = None,
    analyst_coverage_state: str | None = None,
    analyst_coverage_message: str | None = None,
    analyst_operational_status: str | None = None,
    analyst_operational_message: str | None = None,
    analyst_operational_percentage: float | None = None,
    analyst_confidence_count: int | None = None,
    analyst_enabled_confidence_count: int | None = None,
    analyst_confidence_coverage_percentage: float | None = None,
    analyst_enabled_confidence_coverage_percentage: float | None = None,
    analyst_confidence_coverage_state: str | None = None,
    analyst_confidence_coverage_message: str | None = None,
    analyst_enabled_confidence_coverage_state: str | None = None,
    analyst_enabled_confidence_coverage_message: str | None = None,
    analyst_missing_confidence_count: int | None = None,
    analyst_enabled_missing_confidence_count: int | None = None,

) -> RuntimeDashboardStatus:
    return RuntimeDashboardStatus(
        health=make_health(),
        symbol=" nvda ",
        timeframe=" 2M ",
        latest_cycle_status=(
            AnalysisCycleStatus.COMPLETED
        ),
        latest_cycle_message=(
            "Analysis cycle completed."
        ),
        latest_cycle_started_at=NOW,
        latest_cycle_completed_at=(
            NOW
            + timedelta(
                seconds=2,
            )
        ),
        market_session="REGULAR",
        latest_decision="WAIT",
        latest_error_type=None,
        decision_confidence=(
            decision_confidence
        ),
        decision_actionable=(
            decision_actionable
        ),
        decision_recommendation=(
            decision_recommendation
        ),
        decision_reasons=decision_reasons,
        decision_warnings=decision_warnings,
        trade_direction=trade_direction,
        trade_narrative=trade_narrative,
        trade_reasons=trade_reasons,
        trade_warnings=trade_warnings,
        institutional_bias=institutional_bias,
        institutional_bias_confidence=(
            institutional_bias_confidence
        ),
        market_phase=market_phase,
        market_phase_confidence=(
            market_phase_confidence
        ),
        confluence_direction=(
            confluence_direction
        ),
        confluence_score=confluence_score,
        confluence_agreement_count=(
            confluence_agreement_count
        ),
        confluence_conflict_count=(
            confluence_conflict_count
        ),
        confluence_confidence_adjustment=(
            confluence_confidence_adjustment
        ),
        confluence_structure_support=(
            confluence_structure_support
        ),
        confluence_liquidity_support=(
            confluence_liquidity_support
        ),
        confluence_order_block_support=(
            confluence_order_block_support
        ),
        confluence_auction_support=(
            confluence_auction_support
        ),
        confluence_pressure_support=(
            confluence_pressure_support
        ),
        confluence_participation_support=(
            confluence_participation_support
        ),
        confluence_value_support=(
            confluence_value_support
        ),
        confluence_bullish_count=(
            confluence_bullish_count
        ),
        confluence_bearish_count=(
            confluence_bearish_count
        ),
        confluence_neutral_count=(
            confluence_neutral_count
        ),
        confluence_unknown_count=(
            confluence_unknown_count
        ),
        confluence_domain_count=(
            confluence_domain_count
        ),
        market_phase_strength=(
            market_phase_strength
        ),
        market_phase_agreement_count=(
            market_phase_agreement_count
        ),
        market_phase_conflict_count=(
            market_phase_conflict_count
        ),
        market_phase_supporting_domains=(
            market_phase_supporting_domains
        ),
        market_phase_opposing_domains=(
            market_phase_opposing_domains
        ),
        institutional_bias_strength=(
            institutional_bias_strength
        ),
        institutional_bias_bullish_score=(
            institutional_bias_bullish_score
        ),
        institutional_bias_bearish_score=(
            institutional_bias_bearish_score
        ),
        institutional_bias_agreement_count=(
            institutional_bias_agreement_count
        ),
        institutional_bias_conflict_count=(
            institutional_bias_conflict_count
        ),
        institutional_bias_supporting_domains=(
            institutional_bias_supporting_domains
        ),
        institutional_bias_opposing_domains=(
            institutional_bias_opposing_domains
        ),

        setup_lifecycle_state=(
            setup_lifecycle_state
        ),
        setup_lifecycle_direction=(
            setup_lifecycle_direction
        ),
        setup_lifecycle_confidence=(
            setup_lifecycle_confidence
        ),
        setup_lifecycle_atr_distance=(
            setup_lifecycle_atr_distance
        ),
        setup_lifecycle_action=(
            setup_lifecycle_action
        ),
        setup_lifecycle_reason=(
            setup_lifecycle_reason
        ),
        trend_analyst=trend_analyst,
        trend_opinion=trend_opinion,
        trend_confidence=trend_confidence,
        trend_enabled=trend_enabled,
        trend_evidence=trend_evidence,
        trend_warnings=trend_warnings,
        acceptance_confidence=acceptance_confidence,
        analyst_summary=(
        analyst_summary
        if analyst_summary is not None
        else {}
        ),
        structure_analyst=structure_analyst,
        structure_opinion=structure_opinion,
        structure_confidence=structure_confidence,
        structure_enabled=structure_enabled,
        liquidity_analyst=liquidity_analyst,
        liquidity_opinion=liquidity_opinion,
        liquidity_confidence=liquidity_confidence,
        liquidity_enabled=liquidity_enabled,
        order_block_analyst=order_block_analyst,
        order_block_opinion=order_block_opinion,
        order_block_confidence=order_block_confidence,
        order_block_enabled=order_block_enabled,
        auction_analyst=auction_analyst,
        auction_opinion=auction_opinion,
        auction_confidence=auction_confidence,
        auction_enabled=auction_enabled,
        pressure_analyst=pressure_analyst,
        pressure_opinion=pressure_opinion,
        pressure_confidence=pressure_confidence,
        pressure_enabled=pressure_enabled,
        participation_analyst=participation_analyst,
        participation_opinion=participation_opinion,
        participation_confidence=participation_confidence,
        participation_enabled=participation_enabled,
        value_analyst=value_analyst,
        value_opinion=value_opinion,
        value_confidence=value_confidence,
        value_enabled=value_enabled,
        analyst_domain_count=analyst_domain_count,
        analyst_enabled_count=analyst_enabled_count,
        analyst_resolved_count=analyst_resolved_count,
        analyst_average_confidence=(
            analyst_average_confidence
        ),
        analyst_coverage_percentage=(
            analyst_coverage_percentage
        ),
        analyst_coverage_state=(
            analyst_coverage_state
        ),
        analyst_coverage_message=(
            analyst_coverage_message
        ),
        analyst_operational_status=(
            analyst_operational_status
        ),
        analyst_operational_message=(
            analyst_operational_message
        ),
        analyst_operational_percentage=(
            analyst_operational_percentage
        ),
        analyst_enabled_resolved_count=(
            analyst_enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            analyst_enabled_unresolved_count
        ),
        analyst_enabled_average_confidence=(
            analyst_enabled_average_confidence
        ),
        analyst_confidence_count=(
            analyst_confidence_count
        ),
        analyst_enabled_confidence_count=(
            analyst_enabled_confidence_count
        ),
        analyst_confidence_coverage_percentage=(
            analyst_confidence_coverage_percentage
        ),
        analyst_enabled_confidence_coverage_percentage=(
            analyst_enabled_confidence_coverage_percentage
        ),
        analyst_confidence_coverage_state=(
            analyst_confidence_coverage_state
        ),
        analyst_confidence_coverage_message=(
            analyst_confidence_coverage_message
        ),
        analyst_enabled_confidence_coverage_state=(
            analyst_enabled_confidence_coverage_state
        ),
        analyst_enabled_confidence_coverage_message=(
            analyst_enabled_confidence_coverage_message
        ),
        analyst_missing_confidence_count=(
            analyst_missing_confidence_count
        ),
        analyst_enabled_missing_confidence_count=(
            analyst_enabled_missing_confidence_count
        ),
    )


def test_dashboard_status_can_be_created() -> None:
    status = make_status()

    assert status.symbol == "NVDA"
    assert status.timeframe == "2m"

    assert (
        status.latest_cycle_status
        is AnalysisCycleStatus.COMPLETED
    )

    assert status.has_cycle is True
    assert status.cycle_failed is False


def test_dashboard_status_without_cycle() -> None:
    status = RuntimeDashboardStatus(
        health=make_health(),
        symbol="NVDA",
        timeframe="2m",
        latest_cycle_status=None,
        latest_cycle_message=None,
        latest_cycle_started_at=None,
        latest_cycle_completed_at=None,
        market_session=None,
        latest_decision=None,
        latest_error_type=None,
    )

    assert status.has_cycle is False
    assert status.cycle_failed is False


def test_failed_cycle_property() -> None:
    status = RuntimeDashboardStatus(
        health=make_health(),
        symbol="NVDA",
        timeframe="2m",
        latest_cycle_status=(
            AnalysisCycleStatus.FAILED
        ),
        latest_cycle_message=(
            "Provider failed."
        ),
        latest_cycle_started_at=NOW,
        latest_cycle_completed_at=NOW,
        market_session="REGULAR",
        latest_decision=None,
        latest_error_type="RuntimeError",
    )

    assert status.cycle_failed is True


def test_dashboard_status_serializes_to_dictionary() -> None:
    status = make_status()

    payload = status.to_dict()

    assert payload["state"] == "RUNNING"
    assert payload["symbol"] == "NVDA"
    assert payload["timeframe"] == "2m"
    assert (
        payload["latest_cycle_status"]
        == "COMPLETED"
    )
    assert payload["market_session"] == "REGULAR"
    assert payload["latest_decision"] == "WAIT"
    assert payload["has_cycle"] is True
    assert payload["cycle_failed"] is False


def test_dashboard_status_serializes_to_json() -> None:
    status = make_status()

    payload = status.to_json(
        indent=2
    )

    decoded = json.loads(
        payload
    )

    assert decoded == status.to_dict()
    assert "\n" in payload


def test_completed_at_cannot_precede_started_at() -> None:
    with pytest.raises(
        ValueError,
        match="completed_at",
    ):
        RuntimeDashboardStatus(
            health=make_health(),
            symbol="NVDA",
            timeframe="2m",
            latest_cycle_status=(
                AnalysisCycleStatus.FAILED
            ),
            latest_cycle_message=None,
            latest_cycle_started_at=NOW,
            latest_cycle_completed_at=(
                NOW
                - timedelta(
                    seconds=1,
                )
            ),
            market_session=None,
            latest_decision=None,
            latest_error_type=None,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_symbol_cannot_be_empty(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="symbol",
    ):
        RuntimeDashboardStatus(
            health=make_health(),
            symbol=value,
            timeframe="2m",
            latest_cycle_status=None,
            latest_cycle_message=None,
            latest_cycle_started_at=None,
            latest_cycle_completed_at=None,
            market_session=None,
            latest_decision=None,
            latest_error_type=None,
        )

def test_decision_detail_fields_are_serialized() -> None:
    status = make_status(
        decision_confidence=85.0,
        decision_actionable=False,
        decision_recommendation=(
            "Wait for completed-candle acceptance."
        ),
        trade_direction="LONG",
    )

    payload = status.to_dict()

    assert (
        payload["decision_confidence"]
        == 85.0
    )

    assert (
        payload["decision_actionable"]
        is False
    )

    assert (
        payload["decision_recommendation"]
        == "Wait for completed-candle acceptance."
    )

    assert (
        payload["trade_direction"]
        == "LONG"
    )

@pytest.mark.parametrize(
    "confidence",
    (
        -0.01,
        100.01,
    ),
)
def test_decision_confidence_must_be_in_range(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "decision_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            decision_confidence=confidence
        )

def test_decision_actionable_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "decision_actionable must be "
            "a bool or None"
        ),
    ):
        make_status(
            decision_actionable=(
                "yes"  # type: ignore[arg-type]
            )
        )

def test_trade_plan_explanation_fields_are_serialized() -> None:
    status = make_status(
        trade_narrative=(
            "The proposed TradePlan is valid."
        ),
        trade_reasons=(
            "Risk validation passed.",
            "Projected Target 2 provides 2.00R.",
        ),
        trade_warnings=(
            "Position size must respect account risk.",
        ),
    )

    payload = status.to_dict()

    assert (
        payload["trade_narrative"]
        == "The proposed TradePlan is valid."
    )

    assert payload["trade_reasons"] == [
        "Risk validation passed.",
        "Projected Target 2 provides 2.00R.",
    ]

    assert payload["trade_warnings"] == [
        "Position size must respect account risk.",
    ]

def test_trade_plan_explanation_items_are_normalized() -> None:
    status = make_status(
        trade_reasons=(
            "  Risk validation passed.  ",
            "",
            "   ",
        ),
        trade_warnings=(
            "  Review spread before entry.  ",
        ),
    )

    assert status.trade_reasons == (
        "Risk validation passed.",
    )

    assert status.trade_warnings == (
        "Review spread before entry.",
    )

def test_trade_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "trade_reasons must contain "
            "only strings"
        ),
    ):
        make_status(
            trade_reasons=(
                123,  # type: ignore[arg-type]
            )
        )

def test_institutional_context_fields_are_serialized() -> None:
    status = make_status(
        institutional_bias="BULLISH",
        institutional_bias_confidence=88.0,
        market_phase="MARKUP",
        market_phase_confidence=84.0,
        confluence_direction="BULLISH",
        confluence_score=90.0,
        confluence_agreement_count=6,
        confluence_conflict_count=1,
    )

    payload = status.to_dict()

    assert (
        payload["institutional_bias"]
        == "BULLISH"
    )

    assert (
        payload["institutional_bias_confidence"]
        == 88.0
    )

    assert (
        payload["market_phase"]
        == "MARKUP"
    )

    assert (
        payload["market_phase_confidence"]
        == 84.0
    )

    assert (
        payload["confluence_direction"]
        == "BULLISH"
    )

    assert (
        payload["confluence_score"]
        == 90.0
    )

    assert (
        payload["confluence_agreement_count"]
        == 6
    )

    assert (
        payload["confluence_conflict_count"]
        == 1
    )

@pytest.mark.parametrize(
    "field_name",
    (
        "institutional_bias_confidence",
        "market_phase_confidence",
        "confluence_score",
    ),
)
def test_institutional_percentages_must_be_in_range(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        make_status(
            **{
                field_name: 100.01,
            }
        )

@pytest.mark.parametrize(
    "field_name",
    (
        "confluence_agreement_count",
        "confluence_conflict_count",
    ),
)
def test_confluence_counts_cannot_be_negative(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        make_status(
            **{
                field_name: -1,
            }
        )

def test_market_phase_detail_fields_are_serialized() -> None:
    status = make_status(
        market_phase_strength=80.0,
        market_phase_agreement_count=5,
        market_phase_conflict_count=1,
        market_phase_supporting_domains=(
            "STRUCTURE",
            "AUCTION",
            "TREND",
        ),
        market_phase_opposing_domains=(
            "VALUE",
        ),
    )

    payload = status.to_dict()

    assert payload["market_phase_strength"] == 80.0

    assert (
        payload["market_phase_agreement_count"]
        == 5
    )

    assert (
        payload["market_phase_conflict_count"]
        == 1
    )

    assert (
        payload["market_phase_supporting_domains"]
        == [
            "STRUCTURE",
            "AUCTION",
            "TREND",
        ]
    )

    assert (
        payload["market_phase_opposing_domains"]
        == [
            "VALUE",
        ]
    )

def test_market_phase_domain_lists_are_normalized() -> None:
    status = make_status(
        market_phase_supporting_domains=(
            " STRUCTURE ",
            "",
            " TREND ",
        ),
        market_phase_opposing_domains=(
            " VALUE ",
        ),
    )

    assert (
        status.market_phase_supporting_domains
        == (
            "STRUCTURE",
            "TREND",
        )
    )

    assert (
        status.market_phase_opposing_domains
        == (
            "VALUE",
        )
    )

def test_institutional_bias_detail_fields_are_serialized() -> None:
    status = make_status(
        institutional_bias_strength=80.0,
        institutional_bias_bullish_score=90.0,
        institutional_bias_bearish_score=10.0,
        institutional_bias_agreement_count=3,
        institutional_bias_conflict_count=1,
        institutional_bias_supporting_domains=(
            "STRUCTURE",
            "LIQUIDITY",
            "TREND",
        ),
        institutional_bias_opposing_domains=(
            "VALUE",
        ),
    )

    payload = status.to_dict()

    assert (
        payload["institutional_bias_strength"]
        == 80.0
    )

    assert (
        payload["institutional_bias_bullish_score"]
        == 90.0
    )

    assert (
        payload["institutional_bias_bearish_score"]
        == 10.0
    )

    assert (
        payload["institutional_bias_agreement_count"]
        == 3
    )

    assert (
        payload["institutional_bias_conflict_count"]
        == 1
    )

    assert (
        payload["institutional_bias_supporting_domains"]
        == [
            "STRUCTURE",
            "LIQUIDITY",
            "TREND",
        ]
    )

    assert (
        payload["institutional_bias_opposing_domains"]
        == [
            "VALUE",
        ]
    )

def test_institutional_bias_domain_lists_are_normalized() -> None:
    status = make_status(
        institutional_bias_supporting_domains=(
            " STRUCTURE ",
            "",
            " TREND ",
        ),
        institutional_bias_opposing_domains=(
            " VALUE ",
        ),
    )

    assert (
        status.institutional_bias_supporting_domains
        == (
            "STRUCTURE",
            "TREND",
        )
    )

    assert (
        status.institutional_bias_opposing_domains
        == (
            "VALUE",
        )
    )

def test_confluence_detail_fields_are_serialized() -> None:
    status = make_status(
        confluence_confidence_adjustment=8.0,
        confluence_structure_support=True,
        confluence_liquidity_support=True,
        confluence_order_block_support=True,
        confluence_auction_support=False,
        confluence_pressure_support=False,
        confluence_participation_support=False,
        confluence_value_support=False,
        confluence_bullish_count=3,
        confluence_bearish_count=0,
        confluence_neutral_count=0,
        confluence_unknown_count=0,
        confluence_domain_count=3,
    )

    payload = status.to_dict()

    assert (
        payload["confluence_confidence_adjustment"]
        == 8.0
    )

    assert payload["confluence_structure_support"] is True
    assert payload["confluence_liquidity_support"] is True

    assert (
        payload["confluence_order_block_support"]
        is True
    )

    assert payload["confluence_auction_support"] is False
    assert payload["confluence_pressure_support"] is False

    assert (
        payload["confluence_participation_support"]
        is False
    )

    assert payload["confluence_value_support"] is False
    assert payload["confluence_bullish_count"] == 3
    assert payload["confluence_bearish_count"] == 0
    assert payload["confluence_neutral_count"] == 0
    assert payload["confluence_unknown_count"] == 0
    assert payload["confluence_domain_count"] == 3

@pytest.mark.parametrize(
    "value",
    (
        -0.01,
        8.01,
    ),
)
def test_confluence_confidence_adjustment_must_be_in_range(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="between 0 and 8",
    ):
        make_status(
            confluence_confidence_adjustment=value
        )

def test_confluence_support_flags_must_be_bool_or_none() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "confluence_structure_support "
            "must be a bool or None"
        ),
    ):
        make_status(
            confluence_structure_support=(
                1  # type: ignore[arg-type]
            )
        )

def test_status_accepts_setup_lifecycle_detail() -> None:
    status = make_status(
        setup_lifecycle_state="READY",
        setup_lifecycle_direction="long",
        setup_lifecycle_confidence=90.0,
        setup_lifecycle_atr_distance=0.10,
        setup_lifecycle_action="EVALUATE_ENTRY",
        setup_lifecycle_reason=(
            "Setup lifecycle is ready."
        ),
    )

    assert status.setup_lifecycle_state == "READY"
    assert status.setup_lifecycle_direction == "long"
    assert status.setup_lifecycle_confidence == 90.0
    assert status.setup_lifecycle_atr_distance == 0.10
    assert (
        status.setup_lifecycle_action
        == "EVALUATE_ENTRY"
    )
    assert (
        status.setup_lifecycle_reason
        == "Setup lifecycle is ready."
    )

def test_status_serializes_setup_lifecycle_detail() -> None:
    status = make_status(
        setup_lifecycle_state="AT_CORE",
        setup_lifecycle_direction="short",
        setup_lifecycle_confidence=82.0,
        setup_lifecycle_atr_distance=0.25,
        setup_lifecycle_action="PREPARE",
        setup_lifecycle_reason=(
            "Price has returned to core."
        ),
    )

    payload = status.to_dict()

    assert payload["setup_lifecycle_state"] == "AT_CORE"
    assert (
        payload["setup_lifecycle_direction"]
        == "short"
    )
    assert (
        payload["setup_lifecycle_confidence"]
        == 82.0
    )
    assert (
        payload["setup_lifecycle_atr_distance"]
        == 0.25
    )
    assert (
        payload["setup_lifecycle_action"]
        == "PREPARE"
    )
    assert (
        payload["setup_lifecycle_reason"]
        == "Price has returned to core."
    )

@pytest.mark.parametrize(
    "value",
    [
        True,
        "90",
        object(),
    ],
)

def test_status_rejects_invalid_setup_lifecycle_confidence(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="setup_lifecycle_confidence",
    ):
        make_status(
            setup_lifecycle_confidence=value,
        )

@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        100.1,
    ],
)
def test_status_rejects_out_of_range_setup_lifecycle_confidence(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="setup_lifecycle_confidence",
    ):
        make_status(
            setup_lifecycle_confidence=value,
        )

@pytest.mark.parametrize(
    "value",
    [
        True,
        "0.10",
        object(),
    ],
)
def test_status_rejects_invalid_setup_lifecycle_atr_distance(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="setup_lifecycle_atr_distance",
    ):
        make_status(
            setup_lifecycle_atr_distance=value,
        )

def test_status_rejects_negative_setup_lifecycle_atr_distance() -> None:
    with pytest.raises(
        ValueError,
        match="setup_lifecycle_atr_distance",
    ):
        make_status(
            setup_lifecycle_atr_distance=-0.01,
        )

def test_status_accepts_trend_detail() -> None:
    status = make_status(
        trend_analyst="TrendAnalyst",
        trend_opinion="BULLISH",
        trend_confidence=90.0,
        trend_enabled=True,
        trend_evidence=(
            "Price is above EMA9 and VWAP.",
        ),
        trend_warnings=(),
    )

    assert status.trend_analyst == "TrendAnalyst"
    assert status.trend_opinion == "BULLISH"
    assert status.trend_confidence == 90.0
    assert status.trend_enabled is True

    assert status.trend_evidence == (
        "Price is above EMA9 and VWAP.",
    )

    assert status.trend_warnings == ()

def test_status_serializes_trend_detail() -> None:
    status = make_status(
        trend_analyst="TrendAnalyst",
        trend_opinion="BEARISH",
        trend_confidence=82.0,
        trend_enabled=True,
        trend_evidence=(
            "Price is below EMA9.",
            "Price is below VWAP.",
        ),
        trend_warnings=(
            "Trend separation is limited.",
        ),
    )

    payload = status.to_dict()

    assert payload["trend_analyst"] == "TrendAnalyst"
    assert payload["trend_opinion"] == "BEARISH"
    assert payload["trend_confidence"] == 82.0
    assert payload["trend_enabled"] is True

    assert payload["trend_evidence"] == [
        "Price is below EMA9.",
        "Price is below VWAP.",
    ]

    assert payload["trend_warnings"] == [
        "Trend separation is limited.",
    ]

def test_trend_detail_text_and_lists_are_normalized() -> None:
    status = make_status(
        trend_analyst="  TrendAnalyst  ",
        trend_opinion="  BULLISH  ",
        trend_evidence=(
            "  Price is above EMA9.  ",
            "",
            "   ",
            "  EMA9 slope is rising.  ",
        ),
        trend_warnings=(
            "  Price is close to VWAP.  ",
            "",
        ),
    )

    assert status.trend_analyst == "TrendAnalyst"
    assert status.trend_opinion == "BULLISH"

    assert status.trend_evidence == (
        "Price is above EMA9.",
        "EMA9 slope is rising.",
    )

    assert status.trend_warnings == (
        "Price is close to VWAP.",
    )

@pytest.mark.parametrize(
    "value",
    [
        1,
        "yes",
        object(),
    ],
)
def test_status_rejects_invalid_trend_enabled(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="trend_enabled",
    ):
        make_status(
            trend_enabled=value,  # type: ignore[arg-type]
        )

@pytest.mark.parametrize(
    "value",
    [
        True,
        "90",
        object(),
    ],
)
def test_status_rejects_invalid_trend_confidence(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="trend_confidence",
    ):
        make_status(
            trend_confidence=value,  # type: ignore[arg-type]
        )

@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        100.1,
    ],
)
def test_status_rejects_out_of_range_trend_confidence(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="trend_confidence",
    ):
        make_status(
            trend_confidence=value,
        )

def test_status_accepts_decision_rationale() -> None:
    status = make_status(
        decision_reasons=(
            "Directional trend is confirmed.",
            "Setup lifecycle requirements are satisfied.",
        ),
        decision_warnings=(
            "Price is approaching nearby liquidity.",
        ),
    )

    assert status.decision_reasons == (
        "Directional trend is confirmed.",
        "Setup lifecycle requirements are satisfied.",
    )

    assert status.decision_warnings == (
        "Price is approaching nearby liquidity.",
    )

def test_status_serializes_decision_rationale() -> None:
    status = make_status(
        decision_reasons=(
            "Completed-candle acceptance is confirmed.",
        ),
        decision_warnings=(
            "Spread should be reviewed before entry.",
        ),
    )

    payload = status.to_dict()

    assert payload["decision_reasons"] == [
        "Completed-candle acceptance is confirmed.",
    ]

    assert payload["decision_warnings"] == [
        "Spread should be reviewed before entry.",
    ]

def test_decision_rationale_items_are_normalized() -> None:
    status = make_status(
        decision_reasons=(
            "  Trend supports continuation.  ",
            "",
            "   ",
            "  Acceptance is confirmed.  ",
        ),
        decision_warnings=(
            "  Nearby liquidity may reduce available room.  ",
            "",
        ),
    )

    assert status.decision_reasons == (
        "Trend supports continuation.",
        "Acceptance is confirmed.",
    )

    assert status.decision_warnings == (
        "Nearby liquidity may reduce available room.",
    )

def test_decision_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "decision_reasons must contain "
            "only strings"
        ),
    ):
        make_status(
            decision_reasons=(
                123,  # type: ignore[arg-type]
            )
        )

def test_decision_warnings_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "decision_warnings must contain "
            "only strings"
        ),
    ):
        make_status(
            decision_warnings=(
                object(),  # type: ignore[arg-type]
            )
        )

def test_status_accepts_analyst_summary() -> None:
    status = make_status(
        analyst_summary={
            "TREND": {
                "opinion": "Directional trend is bullish.",
                "confidence": 82.0,
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "Sell-side liquidity is active.",
                "confidence": 74.0,
                "enabled": True,
            },
        }
    )

    assert status.analyst_summary == {
        "TREND": {
            "opinion": "Directional trend is bullish.",
            "confidence": 82.0,
            "enabled": True,
        },
        "LIQUIDITY": {
            "opinion": "Sell-side liquidity is active.",
            "confidence": 74.0,
            "enabled": True,
        },
    }

def test_status_normalizes_analyst_summary() -> None:
    status = make_status(
        analyst_summary={
            " trend ": {
                "opinion": "  Bullish continuation.  ",
                "confidence": 81,
                "enabled": True,
            },
            "   ": {
                "opinion": "Ignored",
                "confidence": 50.0,
                "enabled": True,
            },
        }
    )

    assert status.analyst_summary == {
        "TREND": {
            "opinion": "Bullish continuation.",
            "confidence": 81.0,
            "enabled": True,
        },
    }

def test_status_serializes_analyst_summary() -> None:
    status = make_status(
        analyst_summary={
            "ACCEPTANCE": {
                "opinion": "Acceptance is confirmed.",
                "confidence": 88.0,
                "enabled": True,
            },
        }
    )

    payload = status.to_dict()

    assert payload["analyst_summary"] == {
        "ACCEPTANCE": {
            "opinion": "Acceptance is confirmed.",
            "confidence": 88.0,
            "enabled": True,
        },
    }

def test_analyst_summary_must_be_dictionary() -> None:
    with pytest.raises(
        TypeError,
        match="analyst_summary must be a dictionary",
    ):
        make_status(
            analyst_summary=[  # type: ignore[arg-type]
                "TREND"
            ]
        )

def test_analyst_summary_values_must_be_dictionaries() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analyst_summary values must be "
            "dictionaries"
        ),
    ):
        make_status(
            analyst_summary={
                "TREND": "bullish",  # type: ignore[dict-item]
            }
        )

def test_analyst_summary_confidence_must_be_valid() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_summary confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            analyst_summary={
                "TREND": {
                    "opinion": "Bullish",
                    "confidence": 101.0,
                    "enabled": True,
                },
            }
        )

def test_analyst_summary_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analyst_summary enabled must be "
            "a boolean"
        ),
    ):
        make_status(
            analyst_summary={
                "TREND": {
                    "opinion": "Bullish",
                    "confidence": 80.0,
                    "enabled": "yes",
                },
            }
        )

def test_status_accepts_enabled_average_confidence() -> None:
    status = make_status(
        analyst_enabled_average_confidence=82.5,
    )

    assert (
        status.analyst_enabled_average_confidence
        == 82.5
    )

    payload = status.to_dict()

    assert (
        payload["analyst_enabled_average_confidence"]
        == 82.5
    )


@pytest.mark.parametrize(
    "value",
    [
        True,
        "82.5",
        object(),
    ],
)
def test_enabled_average_confidence_must_be_numeric(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_enabled_average_confidence",
    ):
        make_status(
            analyst_enabled_average_confidence=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        100.1,
    ],
)
def test_enabled_average_confidence_must_be_in_range(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_enabled_average_confidence",
    ):
        make_status(
            analyst_enabled_average_confidence=value,
        )

def test_status_accepts_structure_analyst_detail() -> None:
    status = make_status(
        structure_analyst="STRUCTURE",
        structure_opinion=(
            "Bullish structure continuation is confirmed."
        ),
        structure_confidence=84.0,
        structure_enabled=True,
    )

    assert status.structure_analyst == "STRUCTURE"
    assert status.structure_opinion == (
        "Bullish structure continuation is confirmed."
    )
    assert status.structure_confidence == 84.0
    assert status.structure_enabled is True

def test_status_normalizes_structure_text() -> None:
    status = make_status(
        structure_analyst="  STRUCTURE  ",
        structure_opinion=(
            "  Bearish structure remains active.  "
        ),
    )

    assert status.structure_analyst == "STRUCTURE"
    assert status.structure_opinion == (
        "Bearish structure remains active."
    )

def test_status_serializes_structure_analyst_detail() -> None:
    status = make_status(
        structure_analyst="STRUCTURE",
        structure_opinion="Structure is bullish.",
        structure_confidence=79.0,
        structure_enabled=False,
    )

    payload = status.to_dict()

    assert payload["structure_analyst"] == "STRUCTURE"
    assert payload["structure_opinion"] == (
        "Structure is bullish."
    )
    assert payload["structure_confidence"] == 79.0
    assert payload["structure_enabled"] is False

def test_structure_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "structure_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            structure_enabled="yes",  # type: ignore[arg-type]
        )

def test_structure_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "structure_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            structure_confidence="high",  # type: ignore[arg-type]
        )

def test_structure_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "structure_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            structure_confidence=101.0,
        )

def test_status_accepts_liquidity_analyst_detail() -> None:
    status = make_status(
        liquidity_analyst="LIQUIDITY",
        liquidity_opinion=(
            "Sell-side liquidity remains active."
        ),
        liquidity_confidence=78.0,
        liquidity_enabled=True,
    )

    assert status.liquidity_analyst == "LIQUIDITY"

    assert status.liquidity_opinion == (
        "Sell-side liquidity remains active."
    )

    assert status.liquidity_confidence == 78.0
    assert status.liquidity_enabled is True

def test_status_normalizes_liquidity_text() -> None:
    status = make_status(
        liquidity_analyst="  LIQUIDITY  ",
        liquidity_opinion=(
            "  Buy-side liquidity is nearby.  "
        ),
    )

    assert status.liquidity_analyst == "LIQUIDITY"

    assert status.liquidity_opinion == (
        "Buy-side liquidity is nearby."
    )

def test_status_serializes_liquidity_analyst_detail() -> None:
    status = make_status(
        liquidity_analyst="LIQUIDITY",
        liquidity_opinion=(
            "Liquidity conditions are balanced."
        ),
        liquidity_confidence=71.0,
        liquidity_enabled=False,
    )

    payload = status.to_dict()

    assert payload["liquidity_analyst"] == "LIQUIDITY"

    assert payload["liquidity_opinion"] == (
        "Liquidity conditions are balanced."
    )

    assert payload["liquidity_confidence"] == 71.0
    assert payload["liquidity_enabled"] is False

def test_liquidity_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "liquidity_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            liquidity_enabled="yes",  # type: ignore[arg-type]
        )

def test_liquidity_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "liquidity_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            liquidity_confidence="high",  # type: ignore[arg-type]
        )

def test_liquidity_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "liquidity_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            liquidity_confidence=101.0,
        )

def test_status_accepts_order_block_analyst_detail() -> None:
    status = make_status(
        order_block_analyst="ORDER_BLOCK",
        order_block_opinion=(
            "Bullish order block remains valid."
        ),
        order_block_confidence=81.0,
        order_block_enabled=True,
    )

    assert (
        status.order_block_analyst
        == "ORDER_BLOCK"
    )

    assert status.order_block_opinion == (
        "Bullish order block remains valid."
    )

    assert status.order_block_confidence == 81.0
    assert status.order_block_enabled is True

def test_status_normalizes_order_block_text() -> None:
    status = make_status(
        order_block_analyst="  ORDER_BLOCK  ",
        order_block_opinion=(
            "  Price is reacting from a bullish order block.  "
        ),
    )

    assert (
        status.order_block_analyst
        == "ORDER_BLOCK"
    )

    assert status.order_block_opinion == (
        "Price is reacting from a bullish order block."
    )

def test_status_serializes_order_block_analyst_detail() -> None:
    status = make_status(
        order_block_analyst="ORDER_BLOCK",
        order_block_opinion=(
            "Order block support is limited."
        ),
        order_block_confidence=69.0,
        order_block_enabled=False,
    )

    payload = status.to_dict()

    assert (
        payload["order_block_analyst"]
        == "ORDER_BLOCK"
    )

    assert payload["order_block_opinion"] == (
        "Order block support is limited."
    )

    assert payload["order_block_confidence"] == 69.0
    assert payload["order_block_enabled"] is False

def test_order_block_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "order_block_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            order_block_enabled=(
                "yes"  # type: ignore[arg-type]
            ),
        )

def test_order_block_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "order_block_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            order_block_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_order_block_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "order_block_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            order_block_confidence=101.0,
        )

def test_status_accepts_auction_analyst_detail() -> None:
    status = make_status(
        auction_analyst="AUCTION",
        auction_opinion=(
            "Buyers maintain auction control."
        ),
        auction_confidence=79.0,
        auction_enabled=True,
    )

    assert status.auction_analyst == "AUCTION"

    assert status.auction_opinion == (
        "Buyers maintain auction control."
    )

    assert status.auction_confidence == 79.0
    assert status.auction_enabled is True

def test_status_normalizes_auction_text() -> None:
    status = make_status(
        auction_analyst="  AUCTION  ",
        auction_opinion=(
            "  Auction conditions favor buyers.  "
        ),
    )

    assert status.auction_analyst == "AUCTION"

    assert status.auction_opinion == (
        "Auction conditions favor buyers."
    )

def test_status_serializes_auction_analyst_detail() -> None:
    status = make_status(
        auction_analyst="AUCTION",
        auction_opinion=(
            "Auction control remains balanced."
        ),
        auction_confidence=65.0,
        auction_enabled=False,
    )

    payload = status.to_dict()

    assert payload["auction_analyst"] == "AUCTION"

    assert payload["auction_opinion"] == (
        "Auction control remains balanced."
    )

    assert payload["auction_confidence"] == 65.0
    assert payload["auction_enabled"] is False

def test_auction_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "auction_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            auction_enabled=(
                "yes"  # type: ignore[arg-type]
            ),
        )

def test_auction_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "auction_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            auction_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_auction_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "auction_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            auction_confidence=101.0,
        )

def test_status_accepts_pressure_analyst_detail() -> None:
    status = make_status(
        pressure_analyst="PRESSURE",
        pressure_opinion=(
            "Buying pressure remains dominant."
        ),
        pressure_confidence=77.0,
        pressure_enabled=True,
    )

    assert status.pressure_analyst == "PRESSURE"

    assert status.pressure_opinion == (
        "Buying pressure remains dominant."
    )

    assert status.pressure_confidence == 77.0
    assert status.pressure_enabled is True

def test_status_normalizes_pressure_text() -> None:
    status = make_status(
        pressure_analyst="  PRESSURE  ",
        pressure_opinion=(
            "  Selling pressure is weakening.  "
        ),
    )

    assert status.pressure_analyst == "PRESSURE"

    assert status.pressure_opinion == (
        "Selling pressure is weakening."
    )

def test_status_serializes_pressure_analyst_detail() -> None:
    status = make_status(
        pressure_analyst="PRESSURE",
        pressure_opinion=(
            "Pressure conditions remain balanced."
        ),
        pressure_confidence=64.0,
        pressure_enabled=False,
    )

    payload = status.to_dict()

    assert payload["pressure_analyst"] == "PRESSURE"

    assert payload["pressure_opinion"] == (
        "Pressure conditions remain balanced."
    )

    assert payload["pressure_confidence"] == 64.0
    assert payload["pressure_enabled"] is False

def test_pressure_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "pressure_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            pressure_enabled=(
                "yes"  # type: ignore[arg-type]
            ),
        )

def test_pressure_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "pressure_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            pressure_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_pressure_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "pressure_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            pressure_confidence=101.0,
        )

def test_status_accepts_participation_analyst_detail() -> None:
    status = make_status(
        participation_analyst="PARTICIPATION",
        participation_opinion=(
            "Institutional participation is expanding."
        ),
        participation_confidence=76.0,
        participation_enabled=True,
    )

    assert (
        status.participation_analyst
        == "PARTICIPATION"
    )

    assert status.participation_opinion == (
        "Institutional participation is expanding."
    )

    assert status.participation_confidence == 76.0
    assert status.participation_enabled is True

def test_status_normalizes_participation_text() -> None:
    status = make_status(
        participation_analyst=(
            "  PARTICIPATION  "
        ),
        participation_opinion=(
            "  Participation is improving.  "
        ),
    )

    assert (
        status.participation_analyst
        == "PARTICIPATION"
    )

    assert status.participation_opinion == (
        "Participation is improving."
    )

def test_status_serializes_participation_analyst_detail() -> None:
    status = make_status(
        participation_analyst="PARTICIPATION",
        participation_opinion=(
            "Participation remains limited."
        ),
        participation_confidence=62.0,
        participation_enabled=False,
    )

    payload = status.to_dict()

    assert (
        payload["participation_analyst"]
        == "PARTICIPATION"
    )

    assert payload["participation_opinion"] == (
        "Participation remains limited."
    )

    assert (
        payload["participation_confidence"]
        == 62.0
    )

    assert (
        payload["participation_enabled"]
        is False
    )

def test_participation_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "participation_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            participation_enabled=(
                "yes"  # type: ignore[arg-type]
            ),
        )

def test_participation_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "participation_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            participation_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_participation_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "participation_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            participation_confidence=101.0,
        )

def test_status_accepts_value_analyst_detail() -> None:
    status = make_status(
        value_analyst="VALUE",
        value_opinion=(
            "Price remains within fair value."
        ),
        value_confidence=74.0,
        value_enabled=True,
    )

    assert status.value_analyst == "VALUE"

    assert status.value_opinion == (
        "Price remains within fair value."
    )

    assert status.value_confidence == 74.0
    assert status.value_enabled is True

def test_status_normalizes_value_text() -> None:
    status = make_status(
        value_analyst="  VALUE  ",
        value_opinion=(
            "  Price is trading at a discount.  "
        ),
    )

    assert status.value_analyst == "VALUE"

    assert status.value_opinion == (
        "Price is trading at a discount."
    )

def test_status_serializes_value_analyst_detail() -> None:
    status = make_status(
        value_analyst="VALUE",
        value_opinion=(
            "Price is extended above fair value."
        ),
        value_confidence=61.0,
        value_enabled=False,
    )

    payload = status.to_dict()

    assert payload["value_analyst"] == "VALUE"

    assert payload["value_opinion"] == (
        "Price is extended above fair value."
    )

    assert payload["value_confidence"] == 61.0
    assert payload["value_enabled"] is False

def test_value_enabled_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "value_enabled must be "
            "a bool or None"
        ),
    ):
        make_status(
            value_enabled=(
                "yes"  # type: ignore[arg-type]
            ),
        )

def test_value_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "value_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            value_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_value_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "value_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            value_confidence=101.0,
        )

def test_status_accepts_analyst_coverage_summary() -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_enabled_count=8,
        analyst_resolved_count=7,
        analyst_average_confidence=78.5,
    )

    assert status.analyst_domain_count == 8
    assert status.analyst_enabled_count == 8
    assert status.analyst_resolved_count == 7

    assert (
        status.analyst_average_confidence
        == 78.5
    )

def test_status_serializes_analyst_coverage_summary() -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_enabled_count=7,
        analyst_resolved_count=6,
        analyst_average_confidence=74.0,
    )

    payload = status.to_dict()

    assert payload["analyst_domain_count"] == 8
    assert payload["analyst_enabled_count"] == 7
    assert payload["analyst_resolved_count"] == 6

    assert (
        payload["analyst_average_confidence"]
        == 74.0
    )

@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_domain_count",
        "analyst_enabled_count",
        "analyst_resolved_count",
    ],
)
def test_analyst_coverage_counts_must_be_integers(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: 2.5,
            },
        )

@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_domain_count",
        "analyst_enabled_count",
        "analyst_resolved_count",
    ],
)
def test_analyst_coverage_counts_cannot_be_negative(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: -1,
            },
        )

def test_enabled_count_cannot_exceed_domain_count() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_count cannot exceed "
            "analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=7,
            analyst_enabled_count=8,
        )

def test_resolved_count_cannot_exceed_domain_count() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_resolved_count cannot exceed "
            "analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=7,
            analyst_resolved_count=8,
        )

def test_analyst_average_confidence_must_be_numeric() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analyst_average_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            analyst_average_confidence=(
                "high"  # type: ignore[arg-type]
            ),
        )

def test_analyst_average_confidence_must_be_in_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_average_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            analyst_average_confidence=101.0,
        )

def test_status_accepts_analyst_coverage_readiness() -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_resolved_count=6,
        analyst_coverage_percentage=75.0,
        analyst_coverage_state="PARTIAL",
    )

    assert status.analyst_coverage_percentage == 75.0
    assert status.analyst_coverage_state == "PARTIAL"

def test_status_serializes_analyst_coverage_readiness() -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_resolved_count=8,
        analyst_coverage_percentage=100.0,
        analyst_coverage_state="COMPLETE",
    )

    payload = status.to_dict()

    assert payload["analyst_coverage_percentage"] == 100.0
    assert payload["analyst_coverage_state"] == "COMPLETE"

@pytest.mark.parametrize(
    "value",
    [
        True,
        "75",
        object(),
    ],
)

def test_analyst_coverage_percentage_must_be_numeric(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_coverage_percentage",
    ):
        make_status(
            analyst_coverage_percentage=value,  # type: ignore[arg-type]
        )

@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        100.1,
    ],
)

def test_analyst_coverage_percentage_must_be_in_range(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_coverage_percentage",
    ):
        make_status(
            analyst_coverage_percentage=value,
        )

@pytest.mark.parametrize(
    "value",
    [
        "READY",
        "FULL",
        "UNKNOWN",
        "",
    ],
)

def test_analyst_coverage_state_must_be_supported(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_coverage_state",
    ):
        make_status(
            analyst_coverage_state=value,
        )

@pytest.mark.parametrize(
    "value",
    [
        "UNAVAILABLE",
        "UNRESOLVED",
        "PARTIAL",
        "COMPLETE",
    ],
)

def test_analyst_coverage_state_accepts_supported_values(
    value: str,
) -> None:
    status = make_status(
        analyst_coverage_state=value,
    )

    assert status.analyst_coverage_state == value

def test_status_accepts_analyst_confidence_counts(
) -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_enabled_count=5,
        analyst_confidence_count=6,
        analyst_enabled_confidence_count=4,
        analyst_missing_confidence_count=2,
        analyst_enabled_missing_confidence_count=1,
    )

    payload = status.to_dict()

    assert status.analyst_confidence_count == 6
    assert status.analyst_enabled_confidence_count == 4
    assert status.analyst_missing_confidence_count == 2
    assert (
        status.analyst_enabled_missing_confidence_count
        == 1
    )

    assert payload["analyst_confidence_count"] == 6
    assert (
        payload["analyst_enabled_confidence_count"]
        == 4
    )
    assert (
        payload["analyst_missing_confidence_count"]
        == 2
    )
    assert (
        payload[
            "analyst_enabled_missing_confidence_count"
        ]
        == 1
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_confidence_count",
        "analyst_enabled_confidence_count",
        "analyst_missing_confidence_count",
        "analyst_enabled_missing_confidence_count",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        "2",
    ],
)

def test_analyst_confidence_counts_must_be_integers(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_confidence_count",
        "analyst_enabled_confidence_count",
        "analyst_missing_confidence_count",
        "analyst_enabled_missing_confidence_count",
    ],
)

def test_analyst_confidence_counts_cannot_be_negative(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: -1,
            }
        )

def test_status_accepts_analyst_coverage_message(
    ) -> None:
        status = make_status(
            analyst_coverage_state="PARTIAL",
            analyst_coverage_message=(
                "Analyst coverage is partial."
            ),
        )

        assert (
            status.analyst_coverage_state
            == "PARTIAL"
        )
        assert (
            status.analyst_coverage_message
            == "Analyst coverage is partial."
        )

def test_status_normalizes_analyst_coverage_message(
) -> None:
    status = make_status(
        analyst_coverage_state="PARTIAL",
        analyst_coverage_message=(
            "  Analyst coverage is partial.  "
        ),
    )

    assert (
        status.analyst_coverage_state
        == "PARTIAL"
    )
    assert (
        status.analyst_coverage_message
        == "Analyst coverage is partial."
    )

def test_status_converts_empty_analyst_coverage_message_to_none() -> None:
    status = make_status(
        analyst_coverage_message="   ",
    )

    assert status.analyst_coverage_message is None

@pytest.mark.parametrize(
    "value",
    [
        True,
        8,
        object(),
    ],
)
def test_analyst_coverage_message_must_be_string(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_coverage_message",
    ):
        make_status(
            analyst_coverage_message=value,  # type: ignore[arg-type]
        )

def test_status_serializes_analyst_coverage_message(
) -> None:
    status = make_status(
        analyst_coverage_state="PARTIAL",
        analyst_coverage_message=(
            "Analyst coverage is partial."
        ),
    )

    payload = status.to_dict()

    assert (
        payload["analyst_coverage_state"]
        == "PARTIAL"
    )
    assert (
        payload["analyst_coverage_message"]
        == "Analyst coverage is partial."
    )

def test_runtime_dashboard_status_normalizes_analyst_operational_status() -> None:
    status = make_status(
        analyst_operational_status=(
            "  OPERATIONAL  "
        ),
    )

    assert (
        status.analyst_operational_status
        == "OPERATIONAL"
    )


def test_runtime_dashboard_status_normalizes_empty_analyst_operational_status() -> None:
    status = make_status(
        analyst_operational_status="   ",
    )

    assert (
        status.analyst_operational_status
        is None
    )


@pytest.mark.parametrize(
    "value",
    [
        "UNKNOWN",
        "READY",
        "FAILED",
        "operational",
    ],
)
def test_runtime_dashboard_status_rejects_invalid_analyst_operational_status(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_operational_status",
    ):
        make_status(
            analyst_operational_status=value,
        )

def test_runtime_dashboard_status_normalizes_analyst_operational_message(
) -> None:
    status = make_status(
        analyst_operational_status="DEGRADED",
        analyst_operational_message=(
            "  Analyst operations are degraded.  "
        ),
    )

    assert (
        status.analyst_operational_status
        == "DEGRADED"
    )
    assert (
        status.analyst_operational_message
        == "Analyst operations are degraded."
    )

def test_runtime_dashboard_status_normalizes_empty_analyst_operational_message(
) -> None:
    status = make_status(
        analyst_operational_message="   "
    )

    assert (
        status.analyst_operational_message
        is None
    )

def test_runtime_dashboard_status_serializes_analyst_operational_message(
) -> None:
    status = make_status(
        analyst_operational_status="DEGRADED",
        analyst_operational_message=(
            "1 of 2 enabled analyst domains "
            "have produced an opinion."
        ),
    )

    payload = status.to_dict()

    assert (
        payload["analyst_operational_message"]
        == (
            "1 of 2 enabled analyst domains "
            "have produced an opinion."
        )
    )

def test_runtime_dashboard_status_rejects_invalid_analyst_operational_message(
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_operational_message",
    ):
        make_status(
            analyst_operational_message=(
                123  # type: ignore[arg-type]
            )
        )

def test_runtime_dashboard_status_normalizes_analyst_operational_percentage(
) -> None:
    status = make_status(
        analyst_operational_percentage=50
    )

    assert (
        status.analyst_operational_percentage
        == 50.0
    )

    assert isinstance(
        status.analyst_operational_percentage,
        float,
    )

def test_runtime_dashboard_status_serializes_analyst_operational_percentage(
) -> None:
    status = make_status(
        analyst_operational_percentage=75.0
    )

    payload = status.to_dict()

    assert (
        payload["analyst_operational_percentage"]
        == 75.0
    )

@pytest.mark.parametrize(
    "value",
    [
        True,
        "50",
        object(),
    ],
)
def test_runtime_dashboard_status_rejects_invalid_analyst_operational_percentage(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_operational_percentage",
    ):
        make_status(
            analyst_operational_percentage=value,  # type: ignore[arg-type]
        )

@pytest.mark.parametrize(
    "value",
    [
        -0.01,
        100.01,
    ],
)
def test_runtime_dashboard_status_rejects_out_of_range_analyst_operational_percentage(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_operational_percentage",
    ):
        make_status(
            analyst_operational_percentage=value
        )

@pytest.mark.parametrize(
    "value",
    [
        0.0,
        100.0,
    ],
)
def test_runtime_dashboard_status_accepts_analyst_operational_percentage_boundaries(
    value: float,
) -> None:
    status = make_status(
        analyst_operational_percentage=value
    )

    assert (
        status.analyst_operational_percentage
        == value
    )

def test_runtime_dashboard_status_accepts_enabled_resolved_count(
) -> None:
    status = make_status(
        analyst_domain_count=8,
        analyst_enabled_count=6,
        analyst_resolved_count=7,
        analyst_enabled_resolved_count=5,
    )

    assert (
        status.analyst_enabled_resolved_count
        == 5
    )

    payload = status.to_dict()

    assert (
        payload["analyst_enabled_resolved_count"]
        == 5
    )

@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        "1",
        object(),
    ],
)
def test_runtime_dashboard_status_rejects_invalid_enabled_resolved_count(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_enabled_resolved_count",
    ):
        make_status(
            analyst_enabled_resolved_count=value,  # type: ignore[arg-type]
        )

def test_runtime_dashboard_status_rejects_negative_enabled_resolved_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_resolved_count "
            "cannot be negative"
        ),
    ):
        make_status(
            analyst_enabled_resolved_count=-1
        )

def test_enabled_resolved_count_cannot_exceed_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_resolved_count cannot "
            "exceed analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=1,
            analyst_enabled_resolved_count=2,
        )

def test_enabled_resolved_count_cannot_exceed_resolved_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_resolved_count cannot "
            "exceed analyst_resolved_count"
        ),
    ):
        make_status(
            analyst_resolved_count=1,
            analyst_enabled_resolved_count=2,
        )

def test_runtime_dashboard_status_accepts_enabled_unresolved_count(
) -> None:
    status = make_status(
        analyst_enabled_count=6,
        analyst_enabled_resolved_count=4,
        analyst_enabled_unresolved_count=2,
    )

    assert (
        status.analyst_enabled_unresolved_count
        == 2
    )

    payload = status.to_dict()

    assert (
        payload["analyst_enabled_unresolved_count"]
        == 2
    )

@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        "1",
        object(),
    ],
)
def test_runtime_dashboard_status_rejects_invalid_enabled_unresolved_count(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="analyst_enabled_unresolved_count",
    ):
        make_status(
            analyst_enabled_unresolved_count=value,  # type: ignore[arg-type]
        )

def test_runtime_dashboard_status_rejects_negative_enabled_unresolved_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_unresolved_count "
            "cannot be negative"
        ),
    ):
        make_status(
            analyst_enabled_unresolved_count=-1
        )

def test_enabled_unresolved_count_cannot_exceed_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_unresolved_count cannot "
            "exceed analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=1,
            analyst_enabled_unresolved_count=2,
        )

def test_enabled_resolution_counts_must_equal_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "resolved and unresolved counts must equal "
            "analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=4,
            analyst_enabled_resolved_count=2,
            analyst_enabled_unresolved_count=1,
        )

def test_status_accepts_analyst_confidence_coverage(
) -> None:
    status = make_status(
        analyst_confidence_coverage_percentage=75.0,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    payload = status.to_dict()

    assert (
        status.analyst_confidence_coverage_percentage
        == 75.0
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 75.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 50.0
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        True,
        "50.0",
        object(),
    ],
)
def test_analyst_confidence_coverage_must_be_numeric(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        100.1,
    ],
)
def test_analyst_confidence_coverage_must_be_in_range(
    field_name: str,
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        make_status(
            **{
                field_name: value,
            }
        )

def test_status_serializes_analyst_confidence_coverage_fields(
) -> None:
    status = make_status(
        analyst_confidence_coverage_state="PARTIAL",
        analyst_confidence_coverage_message=(
            "Confidence is available for 2 of 4 analysts."
        ),
        analyst_enabled_confidence_coverage_state=(
            "COMPLETE"
        ),
        analyst_enabled_confidence_coverage_message=(
            "Confidence is available for all enabled analysts."
        ),
    )

    payload = status.to_dict()

    assert (
        payload["analyst_confidence_coverage_state"]
        == "PARTIAL"
    )
    assert (
        payload["analyst_confidence_coverage_message"]
        == "Confidence is available for 2 of 4 analysts."
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_state"
        ]
        == "COMPLETE"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == "Confidence is available for all enabled analysts."
    )

@pytest.mark.parametrize(
    "field_name",
    [
        "analyst_confidence_coverage_state",
        "analyst_enabled_confidence_coverage_state",
    ],
)

def test_status_rejects_invalid_confidence_coverage_state(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            rf"{field_name} must be one of"
        ),
    ):
        make_status(
            **{
                field_name: "UNKNOWN",
            }
        )

def test_analyst_confidence_count_cannot_exceed_domain_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_count cannot exceed "
            "analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=2,
            analyst_confidence_count=3,
        )


def test_enabled_confidence_count_cannot_exceed_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_count cannot "
            "exceed analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=1,
            analyst_enabled_confidence_count=2,
        )


def test_analyst_confidence_counts_must_equal_domain_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst confidence and missing confidence "
            "counts must equal analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=8,
            analyst_confidence_count=6,
            analyst_missing_confidence_count=1,
        )


def test_enabled_confidence_counts_must_equal_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst enabled confidence and missing "
            "confidence counts must equal "
            "analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=5,
            analyst_enabled_confidence_count=4,
            analyst_enabled_missing_confidence_count=2,
        )

@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "analyst_domain_count": 8,
            "analyst_confidence_count": 6,
        },
        {
            "analyst_domain_count": 8,
            "analyst_missing_confidence_count": 2,
        },
        {
            "analyst_enabled_count": 5,
            "analyst_enabled_confidence_count": 4,
        },
        {
            "analyst_enabled_count": 5,
            "analyst_enabled_missing_confidence_count": 1,
        },
    ],
)
def test_partial_confidence_count_groups_are_allowed(
    kwargs: dict[str, int],
) -> None:
    status = make_status(
        **kwargs,
    )

    assert status is not None

def test_status_accepts_consistent_confidence_coverage_percentages(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_confidence_count=3,
        analyst_missing_confidence_count=1,
        analyst_confidence_coverage_percentage=75.0,
        analyst_enabled_count=2,
        analyst_enabled_confidence_count=1,
        analyst_enabled_missing_confidence_count=1,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 75.0
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

def test_confidence_coverage_percentage_must_match_counts(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must agree"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_confidence_count=2,
            analyst_confidence_coverage_percentage=75.0,
        )

def test_enabled_confidence_coverage_percentage_must_match_counts(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must agree"
        ),
    ):
        make_status(
            analyst_enabled_count=4,
            analyst_enabled_confidence_count=2,
            analyst_enabled_confidence_coverage_percentage=75.0,
        )

@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "analyst_domain_count": 0,
            "analyst_confidence_count": 0,
            "analyst_confidence_coverage_percentage": 0.0,
        },
        {
            "analyst_enabled_count": 0,
            "analyst_enabled_confidence_count": 0,
            "analyst_enabled_confidence_coverage_percentage": 0.0,
        },
    ],
)

def test_zero_confidence_denominator_requires_zero_percentage(
    kwargs: dict[str, int | float],
) -> None:
    status = make_status(
        **kwargs,
    )

    assert status is not None

@pytest.mark.parametrize(
    (
        "kwargs",
        "expected_message",
    ),
    (
        (
            {
                "analyst_domain_count": 0,
                "analyst_confidence_count": 0,
                "analyst_confidence_coverage_percentage": 75.0,
            },
            (
                "analyst_confidence_coverage_percentage "
                "must be zero when analyst_domain_count "
                "is zero"
            ),
        ),
        (
            {
                "analyst_enabled_count": 0,
                "analyst_enabled_confidence_count": 0,
                "analyst_enabled_confidence_coverage_percentage": 75.0,
            },
            (
                "analyst_enabled_confidence_coverage_percentage "
                "must be zero when analyst_enabled_count "
                "is zero"
            ),
        ),
    ),
)
def test_zero_confidence_denominator_rejects_nonzero_percentage(
    kwargs: dict[str, object],
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            **kwargs,
        )

def test_confidence_coverage_percentage_allows_float_tolerance(
) -> None:
    status = make_status(
        analyst_domain_count=3,
        analyst_confidence_count=1,
        analyst_confidence_coverage_percentage=(
            33.3333333333
        ),
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == pytest.approx(
            33.3333333333
        )
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "confidence_count",
        "expected_state",
    ),
    [
        (0, 0, "UNAVAILABLE"),
        (4, 0, "MISSING"),
        (4, 2, "PARTIAL"),
        (4, 4, "COMPLETE"),
    ],
)

def test_confidence_coverage_state_agrees_with_counts(
    domain_count: int,
    confidence_count: int,
    expected_state: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_confidence_count=confidence_count,
        analyst_confidence_coverage_state=(
            expected_state
        ),
    )

    assert (
        status.analyst_confidence_coverage_state
        == expected_state
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "confidence_count",
        "coverage_state",
        "expected_message",
    ),
    (
        (
            0,
            0,
            "COMPLETE",
            (
                "analyst_confidence_coverage_state must be "
                "UNAVAILABLE or MISSING when "
                "analyst_confidence_count is zero"
            ),
        ),
        (
            4,
            0,
            "PARTIAL",
            (
                "analyst_confidence_coverage_state must be "
                "UNAVAILABLE or MISSING when "
                "analyst_confidence_count is zero"
            ),
        ),
        (
            4,
            2,
            "COMPLETE",
            (
                "analyst_confidence_coverage_state "
                "must agree with analyst_domain_count "
                "and analyst_confidence_count"
            ),
        ),
    ),
)
def test_confidence_coverage_state_rejects_inconsistent_counts(
    domain_count: int,
    confidence_count: int,
    coverage_state: str,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_confidence_count=confidence_count,
            analyst_confidence_coverage_state=coverage_state,
        )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_confidence_count",
        "expected_state",
    ),
    [
        (0, 0, 0, "UNAVAILABLE"),
        (4, 0, 0, "DISABLED"),
        (4, 3, 0, "MISSING"),
        (4, 3, 1, "PARTIAL"),
        (4, 3, 3, "COMPLETE"),
    ],
)

def test_enabled_confidence_coverage_state_agrees_with_counts(
    domain_count: int,
    enabled_count: int,
    enabled_confidence_count: int,
    expected_state: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_confidence_count=(
            enabled_confidence_count
        ),
        analyst_enabled_confidence_coverage_state=(
            expected_state
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == expected_state
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_confidence_count",
        "invalid_state",
        "expected_message",
    ),
    (
        (
            4,
            3,
            0,
            "PARTIAL",
            (
                "analyst_enabled_confidence_coverage_state "
                "must be UNAVAILABLE, DISABLED, or MISSING "
                "when analyst_enabled_confidence_count is zero"
            ),
        ),
        (
            4,
            3,
            1,
            "COMPLETE",
            (
                "analyst_enabled_confidence_coverage_state "
                "must agree"
            ),
        ),
    ),
)
def test_enabled_confidence_coverage_state_rejects_inconsistent_counts(
    domain_count: int,
    enabled_count: int,
    enabled_confidence_count: int,
    invalid_state: str,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_enabled_count=enabled_count,
            analyst_enabled_confidence_count=(
                enabled_confidence_count
            ),
            analyst_enabled_confidence_coverage_state=(
                invalid_state
            ),
        )

@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "analyst_confidence_coverage_state": (
                "PARTIAL"
            ),
        },
        {
            "analyst_domain_count": 4,
            "analyst_confidence_coverage_state": (
                "PARTIAL"
            ),
        },
        {
            "analyst_enabled_confidence_coverage_state": (
                "COMPLETE"
            ),
        },
        {
            "analyst_domain_count": 4,
            "analyst_enabled_count": 2,
            "analyst_enabled_confidence_coverage_state": (
                "COMPLETE"
            ),
        },
    ],
)

def test_partial_confidence_coverage_state_groups_are_allowed(
    kwargs: dict[str, int | str],
) -> None:
    status = make_status(
        **kwargs,
    )

    assert status is not None

def test_missing_confidence_count_cannot_exceed_domain_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_missing_confidence_count cannot "
            "exceed analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_missing_confidence_count=5,
        )

def test_enabled_missing_confidence_count_cannot_exceed_enabled_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_missing_confidence_count "
            "cannot exceed analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=3,
            analyst_enabled_missing_confidence_count=4,
        )

def test_missing_confidence_count_may_equal_domain_count(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_missing_confidence_count=4,
    )

    assert (
        status.analyst_missing_confidence_count
        == 4
    )

def test_enabled_missing_confidence_count_may_equal_enabled_count(
) -> None:
    status = make_status(
        analyst_enabled_count=3,
        analyst_enabled_missing_confidence_count=3,
    )

    assert (
        status.analyst_enabled_missing_confidence_count
        == 3
    )

def test_enabled_confidence_count_cannot_exceed_all_domain_confidence_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_count cannot "
            "exceed analyst_confidence_count"
        ),
    ):
        make_status(
            analyst_confidence_count=3,
            analyst_enabled_confidence_count=4,
        )

def test_enabled_missing_confidence_count_cannot_exceed_all_domain_missing_count(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_missing_confidence_count "
            "cannot exceed "
            "analyst_missing_confidence_count"
        ),
    ):
        make_status(
            analyst_missing_confidence_count=1,
            analyst_enabled_missing_confidence_count=2,
        )

def test_enabled_confidence_count_may_equal_all_domain_confidence_count(
) -> None:
    status = make_status(
        analyst_confidence_count=3,
        analyst_enabled_confidence_count=3,
    )

    assert (
        status.analyst_enabled_confidence_count
        == 3
    )

def test_enabled_missing_confidence_count_may_equal_all_domain_missing_count(
) -> None:
    status = make_status(
        analyst_missing_confidence_count=2,
        analyst_enabled_missing_confidence_count=2,
    )

    assert (
        status.analyst_enabled_missing_confidence_count
        == 2
    )

def test_average_confidence_requires_contributor(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_average_confidence must be None "
            "when analyst_confidence_count is zero"
        ),
    ):
        make_status(
            analyst_confidence_count=0,
            analyst_average_confidence=75.0,
        )

def test_enabled_average_confidence_requires_contributor(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_average_confidence must be "
            "None when "
            "analyst_enabled_confidence_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_confidence_count=0,
            analyst_enabled_average_confidence=75.0,
        )

def test_zero_confidence_contributors_allow_missing_average(
) -> None:
    status = make_status(
        analyst_confidence_count=0,
        analyst_average_confidence=None,
    )

    assert status.analyst_average_confidence is None

def test_zero_enabled_confidence_contributors_allow_missing_average(
) -> None:
    status = make_status(
        analyst_enabled_confidence_count=0,
        analyst_enabled_average_confidence=None,
    )

    assert (
        status.analyst_enabled_average_confidence
        is None
    )

def test_average_confidence_without_contributor_count_is_allowed(
) -> None:
    status = make_status(
        analyst_average_confidence=75.0,
        analyst_enabled_average_confidence=80.0,
    )

    assert status.analyst_average_confidence == 75.0
    assert (
        status.analyst_enabled_average_confidence
        == 80.0
    )

@pytest.mark.parametrize(
    "coverage_state",
    [
        "UNAVAILABLE",
        "MISSING",
    ],
)
def test_average_confidence_rejected_for_noncontributing_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_average_confidence must be None "
            "when analyst_confidence_coverage_state"
        ),
    ):
        make_status(
            analyst_confidence_coverage_state=(
                coverage_state
            ),
            analyst_average_confidence=75.0,
        )

@pytest.mark.parametrize(
    "coverage_state",
    [
        "UNAVAILABLE",
        "DISABLED",
        "MISSING",
    ],
)
def test_enabled_average_confidence_rejected_for_noncontributing_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_average_confidence must be "
            "None when"
        ),
    ):
        make_status(
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
            analyst_enabled_average_confidence=75.0,
        )

@pytest.mark.parametrize(
    "coverage_state",
    [
        "UNAVAILABLE",
        "MISSING",
    ],
)
def test_noncontributing_coverage_state_allows_missing_average(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_confidence_coverage_state=(
            coverage_state
        ),
        analyst_average_confidence=None,
    )

    assert status.analyst_average_confidence is None

@pytest.mark.parametrize(
    "coverage_state",
    [
        "UNAVAILABLE",
        "DISABLED",
        "MISSING",
    ],
)
def test_enabled_noncontributing_state_allows_missing_average(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
        analyst_enabled_average_confidence=None,
    )

    assert (
        status.analyst_enabled_average_confidence
        is None
    )

@pytest.mark.parametrize(
    "coverage_state",
    [
        "PARTIAL",
        "COMPLETE",
    ],
)
def test_contributing_coverage_state_allows_average(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_confidence_coverage_state=(
            coverage_state
        ),
        analyst_average_confidence=75.0,
    )

    assert status.analyst_average_confidence == 75.0

@pytest.mark.parametrize(
    "coverage_state",
    [
        "PARTIAL",
        "COMPLETE",
    ],
)
def test_enabled_contributing_state_allows_average(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
        analyst_enabled_average_confidence=80.0,
    )

    assert (
        status.analyst_enabled_average_confidence
        == 80.0
    )

@pytest.mark.parametrize(
    (
        "coverage_state",
        "coverage_percentage",
    ),
    [
        ("UNAVAILABLE", 0.0),
        ("MISSING", 0.0),
        ("PARTIAL", 25.0),
        ("PARTIAL", 99.9),
        ("COMPLETE", 100.0),
    ],
)
def test_confidence_coverage_state_agrees_with_percentage(
    coverage_state: str,
    coverage_percentage: float,
) -> None:
    status = make_status(
        analyst_confidence_coverage_state=(
            coverage_state
        ),
        analyst_confidence_coverage_percentage=(
            coverage_percentage
        ),
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == coverage_percentage
    )

@pytest.mark.parametrize(
    (
        "coverage_state",
        "coverage_percentage",
    ),
    [
        ("UNAVAILABLE", 10.0),
        ("MISSING", 10.0),
        ("PARTIAL", 0.0),
        ("PARTIAL", 100.0),
        ("COMPLETE", 75.0),
    ],
)
def test_confidence_coverage_state_rejects_inconsistent_percentage(
    coverage_state: str,
    coverage_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must be"
        ),
    ):
        make_status(
            analyst_confidence_coverage_state=(
                coverage_state
            ),
            analyst_confidence_coverage_percentage=(
                coverage_percentage
            ),
        )

@pytest.mark.parametrize(
    (
        "coverage_state",
        "coverage_percentage",
    ),
    [
        ("UNAVAILABLE", 0.0),
        ("DISABLED", 0.0),
        ("MISSING", 0.0),
        ("PARTIAL", 50.0),
        ("COMPLETE", 100.0),
    ],
)
def test_enabled_confidence_coverage_state_agrees_with_percentage(
    coverage_state: str,
    coverage_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
        analyst_enabled_confidence_coverage_percentage=(
            coverage_percentage
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == coverage_percentage
    )

@pytest.mark.parametrize(
    (
        "coverage_state",
        "coverage_percentage",
    ),
    [
        ("UNAVAILABLE", 10.0),
        ("DISABLED", 10.0),
        ("MISSING", 10.0),
        ("PARTIAL", 0.0),
        ("PARTIAL", 100.0),
        ("COMPLETE", 75.0),
    ],
)
def test_enabled_confidence_coverage_state_rejects_inconsistent_percentage(
    coverage_state: str,
    coverage_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must be"
        ),
    ):
        make_status(
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
            analyst_enabled_confidence_coverage_percentage=(
                coverage_percentage
            ),
        )

def test_confidence_coverage_state_or_percentage_alone_is_allowed(
) -> None:
    state_only = make_status(
        analyst_confidence_coverage_state="PARTIAL",
    )
    percentage_only = make_status(
        analyst_confidence_coverage_percentage=50.0,
    )

    assert (
        state_only.analyst_confidence_coverage_state
        == "PARTIAL"
    )
    assert (
        percentage_only.analyst_confidence_coverage_percentage
        == 50.0
    )

def test_average_confidence_rejected_when_domain_count_is_zero(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_average_confidence must be None "
            "when analyst_domain_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_average_confidence=75.0,
        )

def test_enabled_average_confidence_rejected_when_enabled_count_is_zero(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_average_confidence must be "
            "None when analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_count=0,
            analyst_enabled_average_confidence=75.0,
        )

def test_zero_domain_count_allows_missing_average_confidence(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_average_confidence=None,
    )

    assert status.analyst_average_confidence is None

def test_zero_enabled_count_allows_missing_enabled_average_confidence(
) -> None:
    status = make_status(
        analyst_enabled_count=0,
        analyst_enabled_average_confidence=None,
    )

    assert (
        status.analyst_enabled_average_confidence
        is None
    )

def test_positive_analyst_totals_allow_average_confidence(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_average_confidence=75.0,
        analyst_enabled_count=2,
        analyst_enabled_average_confidence=80.0,
    )

    assert status.analyst_average_confidence == 75.0
    assert (
        status.analyst_enabled_average_confidence
        == 80.0
    )

def test_confidence_coverage_percentage_rejected_when_domain_count_is_zero(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must be zero when analyst_domain_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_confidence_coverage_percentage=75.0,
        )

def test_enabled_confidence_coverage_percentage_rejected_when_enabled_count_is_zero(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must be zero when analyst_enabled_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_enabled_count=0,
            analyst_enabled_confidence_coverage_percentage=75.0,
        )

def test_zero_domain_count_allows_zero_confidence_coverage_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_confidence_coverage_percentage=0.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 0.0
    )

def test_zero_enabled_count_allows_zero_enabled_confidence_coverage_percentage(
) -> None:
    status = make_status(
        analyst_enabled_count=0,
        analyst_enabled_confidence_coverage_percentage=0.0,
    )

    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 0.0
    )

def test_positive_analyst_totals_allow_partial_confidence_coverage_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_confidence_coverage_percentage=75.0,
        analyst_enabled_count=2,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 75.0
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

def test_zero_confidence_count_rejects_nonzero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must be zero when analyst_confidence_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_confidence_count=0,
            analyst_confidence_coverage_percentage=40.0,
        )

def test_zero_enabled_confidence_count_rejects_nonzero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must be zero when "
            "analyst_enabled_confidence_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_confidence_count=0,
            analyst_enabled_confidence_coverage_percentage=40.0,
        )

def test_zero_confidence_count_allows_zero_coverage_percentage(
) -> None:
    status = make_status(
        analyst_confidence_count=0,
        analyst_confidence_coverage_percentage=0.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 0.0
    )

def test_zero_enabled_confidence_count_allows_zero_coverage_percentage(
) -> None:
    status = make_status(
        analyst_enabled_confidence_count=0,
        analyst_enabled_confidence_coverage_percentage=0.0,
    )

    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 0.0
    )

def test_positive_confidence_counts_allow_partial_coverage_percentages(
) -> None:
    status = make_status(
        analyst_confidence_count=2,
        analyst_confidence_coverage_percentage=40.0,
        analyst_enabled_confidence_count=1,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 40.0
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_confidence_count_rejects_contributing_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_state must be "
            "UNAVAILABLE or MISSING when "
            "analyst_confidence_count is zero"
        ),
    ):
        make_status(
            analyst_confidence_count=0,
            analyst_confidence_coverage_state=coverage_state,
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_enabled_confidence_count_rejects_contributing_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "must be UNAVAILABLE, DISABLED, or MISSING "
            "when analyst_enabled_confidence_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_confidence_count=0,
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "MISSING",
    ),
)
def test_zero_confidence_count_allows_noncontributing_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_confidence_count=0,
        analyst_confidence_coverage_state=coverage_state,
    )

    assert (
        status.analyst_confidence_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "DISABLED",
        "MISSING",
    ),
)
def test_zero_enabled_confidence_count_allows_noncontributing_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_confidence_count=0,
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == coverage_state
    )

def test_positive_confidence_counts_allow_contributing_coverage_states(
) -> None:
    status = make_status(
        analyst_confidence_count=2,
        analyst_confidence_coverage_state="PARTIAL",
        analyst_enabled_confidence_count=1,
        analyst_enabled_confidence_coverage_state=(
            "COMPLETE"
        ),
    )

    assert (
        status.analyst_confidence_coverage_state
        == "PARTIAL"
    )
    assert (
        status.analyst_enabled_confidence_coverage_state
        == "COMPLETE"
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "MISSING",
    ),
)
def test_positive_confidence_count_rejects_noncontributing_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_state must be "
            "PARTIAL or COMPLETE when "
            "analyst_confidence_count is positive"
        ),
    ):
        make_status(
            analyst_confidence_count=2,
            analyst_confidence_coverage_state=coverage_state,
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "DISABLED",
        "MISSING",
    ),
)
def test_positive_enabled_confidence_count_rejects_noncontributing_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "must be PARTIAL or COMPLETE when "
            "analyst_enabled_confidence_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_confidence_count=1,
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_confidence_count_allows_contributing_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_confidence_count=2,
        analyst_confidence_coverage_state=coverage_state,
    )

    assert (
        status.analyst_confidence_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_enabled_confidence_count_allows_contributing_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_confidence_count=1,
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == coverage_state
    )

def test_contributing_coverage_states_allow_missing_confidence_counts(
) -> None:
    status = make_status(
        analyst_confidence_coverage_state="PARTIAL",
        analyst_enabled_confidence_coverage_state=(
            "COMPLETE"
        ),
    )

    assert (
        status.analyst_confidence_coverage_state
        == "PARTIAL"
    )
    assert (
        status.analyst_enabled_confidence_coverage_state
        == "COMPLETE"
    )

def test_positive_confidence_count_rejects_zero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must be greater than zero when "
            "analyst_confidence_count is positive"
        ),
    ):
        make_status(
            analyst_confidence_count=2,
            analyst_confidence_coverage_percentage=0.0,
        )

def test_positive_enabled_confidence_count_rejects_zero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must be greater than zero when "
            "analyst_enabled_confidence_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_confidence_count=1,
            analyst_enabled_confidence_coverage_percentage=0.0,
        )

def test_positive_confidence_count_allows_positive_coverage_percentage(
) -> None:
    status = make_status(
        analyst_confidence_count=2,
        analyst_confidence_coverage_percentage=25.0,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        == 25.0
    )

def test_positive_enabled_confidence_count_allows_positive_coverage_percentage(
) -> None:
    status = make_status(
        analyst_enabled_confidence_count=1,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

def test_positive_confidence_counts_allow_missing_coverage_percentages(
) -> None:
    status = make_status(
        analyst_confidence_count=2,
        analyst_enabled_confidence_count=1,
    )

    assert (
        status.analyst_confidence_coverage_percentage
        is None
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        is None
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "MISSING",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_domain_count_rejects_nonunavailable_confidence_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_state must be "
            "UNAVAILABLE when analyst_domain_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_confidence_coverage_state=coverage_state,
        )

def test_zero_domain_count_allows_unavailable_confidence_state(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_confidence_coverage_state="UNAVAILABLE",
    )

    assert (
        status.analyst_confidence_coverage_state
        == "UNAVAILABLE"
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "MISSING",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_enabled_count_rejects_nonzero_total_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "must be UNAVAILABLE or DISABLED when "
            "analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_count=0,
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "DISABLED",
    ),
)
def test_zero_enabled_count_allows_zero_total_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_count=0,
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == coverage_state
    )

def test_positive_domain_and_zero_enabled_count_require_disabled_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "must be DISABLED when analyst_domain_count "
            "is positive and analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_enabled_count=0,
            analyst_enabled_confidence_coverage_state=(
                "UNAVAILABLE"
            ),
        )

def test_positive_domain_and_zero_enabled_count_allow_disabled_state(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=0,
        analyst_enabled_confidence_coverage_state=(
            "DISABLED"
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == "DISABLED"
    )

def test_reported_average_confidence_rejects_zero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_percentage "
            "must be greater than zero when "
            "analyst_average_confidence is reported"
        ),
    ):
        make_status(
            analyst_average_confidence=72.0,
            analyst_confidence_coverage_percentage=0.0,
        )

def test_reported_enabled_average_rejects_zero_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_percentage "
            "must be greater than zero when "
            "analyst_enabled_average_confidence is reported"
        ),
    ):
        make_status(
            analyst_enabled_average_confidence=76.0,
            analyst_enabled_confidence_coverage_percentage=0.0,
        )

def test_reported_average_confidence_allows_positive_coverage_percentage(
) -> None:
    status = make_status(
        analyst_average_confidence=72.0,
        analyst_confidence_coverage_percentage=25.0,
    )

    assert status.analyst_average_confidence == 72.0
    assert (
        status.analyst_confidence_coverage_percentage
        == 25.0
    )

def test_reported_enabled_average_allows_positive_coverage_percentage(
) -> None:
    status = make_status(
        analyst_enabled_average_confidence=76.0,
        analyst_enabled_confidence_coverage_percentage=50.0,
    )

    assert (
        status.analyst_enabled_average_confidence
        == 76.0
    )
    assert (
        status.analyst_enabled_confidence_coverage_percentage
        == 50.0
    )

def test_reported_average_confidence_allows_missing_coverage_percentage(
) -> None:
    status = make_status(
        analyst_average_confidence=72.0,
        analyst_enabled_average_confidence=76.0,
    )

    assert status.analyst_average_confidence == 72.0
    assert (
        status.analyst_enabled_average_confidence
        == 76.0
    )

def test_positive_domain_count_rejects_unavailable_confidence_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_state cannot be "
            "UNAVAILABLE when analyst_domain_count is positive"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_confidence_coverage_state="UNAVAILABLE",
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "MISSING",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_domain_count_allows_available_confidence_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_confidence_coverage_state=coverage_state,
    )

    assert (
        status.analyst_confidence_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "DISABLED",
    ),
)
def test_positive_enabled_count_rejects_inactive_confidence_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "cannot be UNAVAILABLE or DISABLED when "
            "analyst_enabled_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_count=3,
            analyst_enabled_confidence_coverage_state=(
                coverage_state
            ),
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "MISSING",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_enabled_count_allows_active_confidence_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_enabled_count=3,
        analyst_enabled_confidence_coverage_state=(
            coverage_state
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_state
        == coverage_state
    )

def test_positive_analyst_totals_allow_missing_coverage_states(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=3,
    )

    assert (
        status.analyst_confidence_coverage_state
        is None
    )
    assert (
        status.analyst_enabled_confidence_coverage_state
        is None
    )

def test_confidence_coverage_message_requires_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_message "
            "requires analyst_confidence_coverage_state"
        ),
    ):
        make_status(
            analyst_confidence_coverage_message=(
                "Confidence coverage is partial."
            ),
        )

def test_enabled_confidence_coverage_message_requires_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_message "
            "requires "
            "analyst_enabled_confidence_coverage_state"
        ),
    ):
        make_status(
            analyst_enabled_confidence_coverage_message=(
                "Enabled confidence coverage is partial."
            ),
        )

def test_confidence_coverage_state_allows_message(
) -> None:
    status = make_status(
        analyst_confidence_coverage_state="PARTIAL",
        analyst_confidence_coverage_message=(
            "Confidence coverage is partial."
        ),
    )

    assert (
        status.analyst_confidence_coverage_message
        == "Confidence coverage is partial."
    )

def test_enabled_confidence_coverage_state_allows_message(
) -> None:
    status = make_status(
        analyst_enabled_confidence_coverage_state=(
            "COMPLETE"
        ),
        analyst_enabled_confidence_coverage_message=(
            "Enabled confidence coverage is complete."
        ),
    )

    assert (
        status.analyst_enabled_confidence_coverage_message
        == "Enabled confidence coverage is complete."
    )

def test_confidence_coverage_states_allow_missing_messages(
) -> None:
    status = make_status(
        analyst_confidence_coverage_state="PARTIAL",
        analyst_enabled_confidence_coverage_state=(
            "COMPLETE"
        ),
    )

    assert (
        status.analyst_confidence_coverage_message
        is None
    )
    assert (
        status.analyst_enabled_confidence_coverage_message
        is None
    )

def test_blank_confidence_coverage_messages_normalize_to_none(
) -> None:
    status = make_status(
        analyst_confidence_coverage_message="   ",
        analyst_enabled_confidence_coverage_message="\t",
    )

    assert (
        status.analyst_confidence_coverage_message
        is None
    )
    assert (
        status.analyst_enabled_confidence_coverage_message
        is None
    )

def test_analyst_coverage_message_requires_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_message requires "
            "analyst_coverage_state"
        ),
    ):
        make_status(
            analyst_coverage_message=(
                "Analyst coverage is partial."
            ),
        )

def test_analyst_operational_message_requires_status(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_message requires "
            "analyst_operational_status"
        ),
    ):
        make_status(
            analyst_operational_message=(
                "Analyst operations are degraded."
            ),
        )

def test_analyst_coverage_state_allows_message(
) -> None:
    status = make_status(
        analyst_coverage_state="PARTIAL",
        analyst_coverage_message=(
            "Analyst coverage is partial."
        ),
    )

    assert (
        status.analyst_coverage_message
        == "Analyst coverage is partial."
    )

def test_analyst_operational_status_allows_message(
) -> None:
    status = make_status(
        analyst_operational_status="DEGRADED",
        analyst_operational_message=(
            "Analyst operations are degraded."
        ),
    )

    assert (
        status.analyst_operational_message
        == "Analyst operations are degraded."
    )

def test_analyst_states_allow_missing_messages(
) -> None:
    status = make_status(
        analyst_coverage_state="PARTIAL",
        analyst_operational_status="DEGRADED",
    )

    assert status.analyst_coverage_message is None
    assert status.analyst_operational_message is None

def test_blank_analyst_status_messages_normalize_to_none(
) -> None:
    status = make_status(
        analyst_coverage_message="   ",
        analyst_operational_message="\t",
    )

    assert status.analyst_coverage_message is None
    assert status.analyst_operational_message is None

@pytest.mark.parametrize(
    (
        "coverage_state",
        "coverage_percentage",
    ),
    (
        (
            "UNAVAILABLE",
            0.0,
        ),
        (
            "UNRESOLVED",
            0.0,
        ),
        (
            "PARTIAL",
            25.0,
        ),
        (
            "PARTIAL",
            75.0,
        ),
        (
            "COMPLETE",
            100.0,
        ),
    ),
)
def test_analyst_coverage_state_accepts_consistent_percentage(
    coverage_state: str,
    coverage_percentage: float,
) -> None:
    status = make_status(
        analyst_coverage_state=coverage_state,
        analyst_coverage_percentage=(
            coverage_percentage
        ),
    )

    assert (
        status.analyst_coverage_state
        == coverage_state
    )
    assert (
        status.analyst_coverage_percentage
        == coverage_percentage
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "UNRESOLVED",
    ),
)
def test_noncontributing_analyst_coverage_state_rejects_nonzero_percentage(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must be zero "
            "when analyst_coverage_state is "
            "UNAVAILABLE or UNRESOLVED"
        ),
    ):
        make_status(
            analyst_coverage_state=coverage_state,
            analyst_coverage_percentage=25.0,
        )

@pytest.mark.parametrize(
    "coverage_percentage",
    (
        0.0,
        100.0,
    ),
)
def test_partial_analyst_coverage_state_rejects_boundary_percentage(
    coverage_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must be greater "
            "than zero and less than 100 when "
            "analyst_coverage_state is PARTIAL"
        ),
    ):
        make_status(
            analyst_coverage_state="PARTIAL",
            analyst_coverage_percentage=(
                coverage_percentage
            ),
        )

def test_complete_analyst_coverage_state_rejects_incomplete_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must be 100 "
            "when analyst_coverage_state is COMPLETE"
        ),
    ):
        make_status(
            analyst_coverage_state="COMPLETE",
            analyst_coverage_percentage=75.0,
        )

def test_analyst_coverage_state_and_percentage_allow_partial_construction(
) -> None:
    state_only = make_status(
        analyst_coverage_state="PARTIAL",
    )
    percentage_only = make_status(
        analyst_coverage_percentage=50.0,
    )

    assert (
        state_only.analyst_coverage_percentage
        is None
    )
    assert (
        percentage_only.analyst_coverage_state
        is None
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "resolved_count",
        "coverage_percentage",
    ),
    (
        (
            0,
            0,
            0.0,
        ),
        (
            4,
            0,
            0.0,
        ),
        (
            4,
            1,
            25.0,
        ),
        (
            4,
            2,
            50.0,
        ),
        (
            4,
            4,
            100.0,
        ),
    ),
)
def test_analyst_coverage_percentage_accepts_consistent_counts(
    domain_count: int,
    resolved_count: int,
    coverage_percentage: float,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_resolved_count=resolved_count,
        analyst_coverage_percentage=coverage_percentage,
    )

    assert (
        status.analyst_coverage_percentage
        == coverage_percentage
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "resolved_count",
        "coverage_percentage",
    ),
    (
        (
            0,
            0,
            25.0,
        ),
        (
            4,
            0,
            25.0,
        ),
        (
            4,
            1,
            50.0,
        ),
        (
            4,
            2,
            75.0,
        ),
        (
            4,
            4,
            75.0,
        ),
    ),
)
def test_analyst_coverage_percentage_rejects_inconsistent_counts(
    domain_count: int,
    resolved_count: int,
    coverage_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must agree "
            "with analyst_resolved_count and "
            "analyst_domain_count"
        ),
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_resolved_count=resolved_count,
            analyst_coverage_percentage=coverage_percentage,
        )

def test_analyst_coverage_percentage_allows_missing_count_inputs(
) -> None:
    domain_only = make_status(
        analyst_domain_count=4,
        analyst_coverage_percentage=50.0,
    )
    resolved_only = make_status(
        analyst_resolved_count=2,
        analyst_coverage_percentage=50.0,
    )

    assert (
        domain_only.analyst_coverage_percentage
        == 50.0
    )
    assert (
        resolved_only.analyst_coverage_percentage
        == 50.0
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "resolved_count",
        "coverage_state",
    ),
    (
        (
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            0,
            "UNRESOLVED",
        ),
        (
            4,
            1,
            "PARTIAL",
        ),
        (
            4,
            3,
            "PARTIAL",
        ),
        (
            4,
            4,
            "COMPLETE",
        ),
    ),
)
def test_analyst_coverage_state_accepts_consistent_counts(
    domain_count: int,
    resolved_count: int,
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_resolved_count=resolved_count,
        analyst_coverage_state=coverage_state,
    )

    assert (
        status.analyst_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "resolved_count",
        "invalid_state",
    ),
    (
        (
            0,
            0,
            "UNRESOLVED",
        ),
        (
            4,
            0,
            "PARTIAL",
        ),
        (
            4,
            1,
            "UNRESOLVED",
        ),
        (
            4,
            2,
            "COMPLETE",
        ),
        (
            4,
            4,
            "PARTIAL",
        ),
    ),
)
def test_analyst_coverage_state_rejects_inconsistent_counts(
    domain_count: int,
    resolved_count: int,
    invalid_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_state must agree "
            "with analyst_domain_count and "
            "analyst_resolved_count"
        ),
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_resolved_count=resolved_count,
            analyst_coverage_state=invalid_state,
        )

def test_analyst_coverage_state_allows_missing_count_inputs(
) -> None:
    domain_only = make_status(
        analyst_domain_count=4,
        analyst_coverage_state="PARTIAL",
    )
    resolved_only = make_status(
        analyst_resolved_count=2,
        analyst_coverage_state="PARTIAL",
    )

    assert (
        domain_only.analyst_coverage_state
        == "PARTIAL"
    )
    assert (
        resolved_only.analyst_coverage_state
        == "PARTIAL"
    )

@pytest.mark.parametrize(
    (
        "operational_status",
        "operational_percentage",
    ),
    (
        (
            "UNAVAILABLE",
            0.0,
        ),
        (
            "DISABLED",
            0.0,
        ),
        (
            "UNRESOLVED",
            0.0,
        ),
        (
            "DEGRADED",
            25.0,
        ),
        (
            "DEGRADED",
            75.0,
        ),
        (
            "OPERATIONAL",
            100.0,
        ),
    ),
)
def test_analyst_operational_status_accepts_consistent_percentage(
    operational_status: str,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_operational_status=operational_status,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )
    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
        "UNRESOLVED",
    ),
)
def test_inactive_operational_status_rejects_nonzero_percentage(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be zero "
            "when analyst_operational_status is "
            "UNAVAILABLE, DISABLED, or UNRESOLVED"
        ),
    ):
        make_status(
            analyst_operational_status=operational_status,
            analyst_operational_percentage=25.0,
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        100.0,
    ),
)
def test_degraded_operational_status_rejects_boundary_percentage(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be greater "
            "than zero and less than 100 when "
            "analyst_operational_status is DEGRADED"
        ),
    ):
        make_status(
            analyst_operational_status="DEGRADED",
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

def test_operational_status_rejects_incomplete_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be 100 "
            "when analyst_operational_status is OPERATIONAL"
        ),
    ):
        make_status(
            analyst_operational_status="OPERATIONAL",
            analyst_operational_percentage=75.0,
        )

def test_operational_status_and_percentage_allow_partial_construction(
) -> None:
    status_only = make_status(
        analyst_operational_status="DEGRADED",
    )
    percentage_only = make_status(
        analyst_operational_percentage=50.0,
    )

    assert (
        status_only.analyst_operational_percentage
        is None
    )
    assert (
        percentage_only.analyst_operational_status
        is None
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "operational_percentage",
    ),
    (
        (
            0,
            0,
            0.0,
        ),
        (
            4,
            0,
            0.0,
        ),
        (
            4,
            1,
            25.0,
        ),
        (
            4,
            2,
            50.0,
        ),
        (
            4,
            4,
            100.0,
        ),
    ),
)
def test_analyst_operational_percentage_accepts_consistent_counts(
    enabled_count: int,
    enabled_resolved_count: int,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "operational_percentage",
    ),
    (
        (
            0,
            0,
            25.0,
        ),
        (
            4,
            0,
            25.0,
        ),
        (
            4,
            1,
            50.0,
        ),
        (
            4,
            2,
            75.0,
        ),
        (
            4,
            4,
            75.0,
        ),
    ),
)
def test_analyst_operational_percentage_rejects_inconsistent_counts(
    enabled_count: int,
    enabled_resolved_count: int,
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must agree "
            "with analyst_enabled_resolved_count and "
            "analyst_enabled_count"
        ),
    ):
        make_status(
            analyst_enabled_count=enabled_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

def test_analyst_operational_percentage_allows_missing_count_inputs(
) -> None:
    enabled_total_only = make_status(
        analyst_enabled_count=4,
        analyst_operational_percentage=50.0,
    )
    enabled_resolved_only = make_status(
        analyst_enabled_resolved_count=2,
        analyst_operational_percentage=50.0,
    )

    assert (
        enabled_total_only.analyst_operational_percentage
        == 50.0
    )
    assert (
        enabled_resolved_only.analyst_operational_percentage
        == 50.0
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_resolved_count",
        "operational_status",
    ),
    (
        (
            0,
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            0,
            0,
            "DISABLED",
        ),
        (
            4,
            3,
            0,
            "UNRESOLVED",
        ),
        (
            4,
            3,
            1,
            "DEGRADED",
        ),
        (
            4,
            3,
            2,
            "DEGRADED",
        ),
        (
            4,
            3,
            3,
            "OPERATIONAL",
        ),
    ),
)
def test_analyst_operational_status_accepts_consistent_counts(
    domain_count: int,
    enabled_count: int,
    enabled_resolved_count: int,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_resolved_count",
        "invalid_status",
    ),
    (
        (
            0,
            0,
            0,
            "DISABLED",
        ),
        (
            4,
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            3,
            0,
            "DEGRADED",
        ),
        (
            4,
            3,
            1,
            "UNRESOLVED",
        ),
        (
            4,
            3,
            2,
            "OPERATIONAL",
        ),
        (
            4,
            3,
            3,
            "DEGRADED",
        ),
    ),
)
def test_analyst_operational_status_rejects_inconsistent_counts(
    domain_count: int,
    enabled_count: int,
    enabled_resolved_count: int,
    invalid_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must agree "
            "with analyst_domain_count, "
            "analyst_enabled_count, and "
            "analyst_enabled_resolved_count"
        ),
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_enabled_count=enabled_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_operational_status=(
                invalid_status
            ),
        )

def test_analyst_operational_status_allows_missing_count_inputs(
) -> None:
    domain_only = make_status(
        analyst_domain_count=4,
        analyst_operational_status="DEGRADED",
    )
    enabled_only = make_status(
        analyst_enabled_count=3,
        analyst_operational_status="DEGRADED",
    )
    resolved_only = make_status(
        analyst_enabled_resolved_count=2,
        analyst_operational_status="DEGRADED",
    )

    assert (
        domain_only.analyst_operational_status
        == "DEGRADED"
    )
    assert (
        enabled_only.analyst_operational_status
        == "DEGRADED"
    )
    assert (
        resolved_only.analyst_operational_status
        == "DEGRADED"
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "DISABLED",
        "UNRESOLVED",
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_zero_domain_count_rejects_available_operational_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "UNAVAILABLE when analyst_domain_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_operational_status=operational_status,
        )

def test_zero_domain_count_allows_unavailable_operational_status(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_operational_status="UNAVAILABLE",
    )

    assert status.analyst_domain_count == 0
    assert (
        status.analyst_operational_status
        == "UNAVAILABLE"
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNRESOLVED",
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_zero_enabled_count_rejects_active_operational_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "UNAVAILABLE or DISABLED when "
            "analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_count=0,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
    ),
)
def test_zero_enabled_count_allows_inactive_operational_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_count=0,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

def test_positive_domain_and_zero_enabled_count_require_disabled_status(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "DISABLED when analyst_domain_count is "
            "positive and analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_enabled_count=0,
            analyst_operational_status="UNAVAILABLE",
        )

def test_positive_domain_and_zero_enabled_count_allow_disabled_status(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=0,
        analyst_operational_status="DISABLED",
    )

    assert (
        status.analyst_operational_status
        == "DISABLED"
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
    ),
)
def test_positive_enabled_count_rejects_inactive_operational_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status cannot be "
            "UNAVAILABLE or DISABLED when "
            "analyst_enabled_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_count=3,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNRESOLVED",
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_positive_enabled_count_allows_active_operational_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_count=3,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_zero_enabled_resolved_count_rejects_resolved_operational_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "UNAVAILABLE, DISABLED, or UNRESOLVED "
            "when analyst_enabled_resolved_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_enabled_resolved_count=0,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
        "UNRESOLVED",
    ),
)
def test_zero_enabled_resolved_count_allows_unresolved_operational_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=0,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
        "UNRESOLVED",
    ),
)
def test_positive_enabled_resolved_count_rejects_unresolved_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "DEGRADED or OPERATIONAL when "
            "analyst_enabled_resolved_count "
            "is positive"
        ),
    ):
        make_status(
            analyst_enabled_resolved_count=2,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_positive_enabled_resolved_count_allows_resolved_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=2,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

def test_enabled_resolved_count_allows_missing_operational_status(
) -> None:
    zero_resolved = make_status(
        analyst_enabled_resolved_count=0,
    )
    positive_resolved = make_status(
        analyst_enabled_resolved_count=2,
    )

    assert (
        zero_resolved.analyst_operational_status
        is None
    )
    assert (
        positive_resolved.analyst_operational_status
        is None
    )

def test_zero_enabled_count_rejects_nonzero_operational_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be zero "
            "when analyst_enabled_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_count=0,
            analyst_operational_percentage=50.0,
        )

def test_zero_enabled_resolved_count_rejects_nonzero_operational_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be zero "
            "when analyst_enabled_resolved_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_resolved_count=0,
            analyst_operational_percentage=25.0,
        )

def test_zero_enabled_count_allows_zero_operational_percentage(
) -> None:
    status = make_status(
        analyst_enabled_count=0,
        analyst_operational_percentage=0.0,
    )

    assert (
        status.analyst_operational_percentage
        == 0.0
    )

def test_zero_enabled_resolved_count_allows_zero_operational_percentage(
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=0,
        analyst_operational_percentage=0.0,
    )

    assert (
        status.analyst_operational_percentage
        == 0.0
    )

def test_positive_enabled_count_allows_zero_operational_percentage(
) -> None:
    status = make_status(
        analyst_enabled_count=3,
        analyst_operational_percentage=0.0,
    )

    assert (
        status.analyst_operational_percentage
        == 0.0
    )

def test_zero_operational_counts_allow_missing_percentage(
) -> None:
    enabled_total = make_status(
        analyst_enabled_count=0,
    )
    enabled_resolved = make_status(
        analyst_enabled_resolved_count=0,
    )

    assert (
        enabled_total.analyst_operational_percentage
        is None
    )
    assert (
        enabled_resolved.analyst_operational_percentage
        is None
    )

def test_positive_enabled_resolved_count_rejects_zero_operational_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be "
            "greater than zero when "
            "analyst_enabled_resolved_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_resolved_count=2,
            analyst_operational_percentage=0.0,
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        25.0,
        50.0,
        100.0,
    ),
)
def test_positive_enabled_resolved_count_allows_positive_percentage(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=2,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

def test_positive_enabled_resolved_count_allows_missing_percentage(
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=2,
    )

    assert (
        status.analyst_operational_percentage
        is None
    )

def test_positive_operational_percentage_allows_missing_resolved_count(
) -> None:
    status = make_status(
        analyst_operational_percentage=50.0,
    )

    assert (
        status.analyst_enabled_resolved_count
        is None
    )

def test_zero_domain_count_rejects_nonzero_analyst_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must be zero "
            "when analyst_domain_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_coverage_percentage=50.0,
        )

def test_zero_resolved_count_rejects_nonzero_analyst_coverage_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_percentage must be zero "
            "when analyst_resolved_count is zero"
        ),
    ):
        make_status(
            analyst_resolved_count=0,
            analyst_coverage_percentage=25.0,
        )

def test_zero_domain_count_allows_zero_analyst_coverage_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_coverage_percentage=0.0,
    )

    assert (
        status.analyst_coverage_percentage
        == 0.0
    )

def test_zero_resolved_count_allows_zero_analyst_coverage_percentage(
) -> None:
    status = make_status(
        analyst_resolved_count=0,
        analyst_coverage_percentage=0.0,
    )

    assert (
        status.analyst_coverage_percentage
        == 0.0
    )

def test_positive_domain_count_allows_zero_analyst_coverage_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_coverage_percentage=0.0,
    )

    assert (
        status.analyst_coverage_percentage
        == 0.0
    )

def test_zero_analyst_coverage_counts_allow_missing_percentage(
) -> None:
    domain_total = make_status(
        analyst_domain_count=0,
    )
    resolved_total = make_status(
        analyst_resolved_count=0,
    )

    assert (
        domain_total.analyst_coverage_percentage
        is None
    )
    assert (
        resolved_total.analyst_coverage_percentage
        is None
    )

@pytest.mark.parametrize(
    "coverage_percentage",
    (
        25.0,
        50.0,
        100.0,
    ),
)
def test_positive_resolved_count_allows_positive_coverage_percentage(
    coverage_percentage: float,
) -> None:
    status = make_status(
        analyst_resolved_count=2,
        analyst_coverage_percentage=(
            coverage_percentage
        ),
    )

    assert (
        status.analyst_coverage_percentage
        == coverage_percentage
    )

def test_positive_resolved_count_allows_missing_coverage_percentage(
) -> None:
    status = make_status(
        analyst_resolved_count=2,
    )

    assert (
        status.analyst_coverage_percentage
        is None
    )

def test_positive_coverage_percentage_allows_missing_resolved_count(
) -> None:
    status = make_status(
        analyst_coverage_percentage=50.0,
    )

    assert (
        status.analyst_resolved_count
        is None
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNRESOLVED",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_domain_count_rejects_available_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_state must be "
            "UNAVAILABLE when analyst_domain_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_coverage_state=coverage_state,
        )

def test_zero_domain_count_allows_unavailable_coverage_state(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_coverage_state="UNAVAILABLE",
    )

    assert (
        status.analyst_coverage_state
        == "UNAVAILABLE"
    )

def test_positive_domain_count_rejects_unavailable_coverage_state(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_state cannot be "
            "UNAVAILABLE when analyst_domain_count "
            "is positive"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_coverage_state="UNAVAILABLE",
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNRESOLVED",
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_domain_count_allows_available_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_coverage_state=coverage_state,
    )

    assert (
        status.analyst_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_zero_resolved_count_rejects_resolved_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_state must be "
            "UNAVAILABLE or UNRESOLVED when "
            "analyst_resolved_count is zero"
        ),
    ):
        make_status(
            analyst_resolved_count=0,
            analyst_coverage_state=coverage_state,
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "UNRESOLVED",
    ),
)
def test_zero_resolved_count_allows_unresolved_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_resolved_count=0,
        analyst_coverage_state=coverage_state,
    )

    assert (
        status.analyst_coverage_state
        == coverage_state
    )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "UNAVAILABLE",
        "UNRESOLVED",
    ),
)
def test_positive_resolved_count_rejects_unresolved_coverage_state(
    coverage_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_coverage_state must be "
            "PARTIAL or COMPLETE when "
            "analyst_resolved_count is positive"
        ),
    ):
        make_status(
            analyst_resolved_count=2,
            analyst_coverage_state=coverage_state,
        )

@pytest.mark.parametrize(
    "coverage_state",
    (
        "PARTIAL",
        "COMPLETE",
    ),
)
def test_positive_resolved_count_allows_resolved_coverage_state(
    coverage_state: str,
) -> None:
    status = make_status(
        analyst_resolved_count=2,
        analyst_coverage_state=coverage_state,
    )

    assert (
        status.analyst_coverage_state
        == coverage_state
    )

def test_analyst_coverage_counts_allow_missing_state(
) -> None:
    zero_domain = make_status(
        analyst_domain_count=0,
    )
    positive_domain = make_status(
        analyst_domain_count=4,
    )
    zero_resolved = make_status(
        analyst_resolved_count=0,
    )
    positive_resolved = make_status(
        analyst_resolved_count=2,
    )

    assert zero_domain.analyst_coverage_state is None
    assert positive_domain.analyst_coverage_state is None
    assert zero_resolved.analyst_coverage_state is None
    assert positive_resolved.analyst_coverage_state is None

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNRESOLVED",
        "DEGRADED",
    ),
)
def test_zero_enabled_unresolved_count_rejects_unresolved_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "UNAVAILABLE, DISABLED, or OPERATIONAL "
            "when analyst_enabled_unresolved_count "
            "is zero"
        ),
    ):
        make_status(
            analyst_enabled_unresolved_count=0,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
        "OPERATIONAL",
    ),
)
def test_zero_enabled_unresolved_count_allows_resolved_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_unresolved_count=0,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNAVAILABLE",
        "DISABLED",
        "OPERATIONAL",
    ),
)
def test_positive_enabled_unresolved_count_rejects_resolved_status(
    operational_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must be "
            "UNRESOLVED or DEGRADED when "
            "analyst_enabled_unresolved_count "
            "is positive"
        ),
    ):
        make_status(
            analyst_enabled_unresolved_count=2,
            analyst_operational_status=(
                operational_status
            ),
        )

@pytest.mark.parametrize(
    "operational_status",
    (
        "UNRESOLVED",
        "DEGRADED",
    ),
)
def test_positive_enabled_unresolved_count_allows_unresolved_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_unresolved_count=2,
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

def test_enabled_unresolved_count_allows_missing_operational_status(
) -> None:
    zero_unresolved = make_status(
        analyst_enabled_unresolved_count=0,
    )
    positive_unresolved = make_status(
        analyst_enabled_unresolved_count=2,
    )

    assert (
        zero_unresolved.analyst_operational_status
        is None
    )
    assert (
        positive_unresolved.analyst_operational_status
        is None
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_unresolved_count",
        "operational_percentage",
    ),
    (
        (
            0,
            0,
            0.0,
        ),
        (
            4,
            4,
            0.0,
        ),
        (
            4,
            3,
            25.0,
        ),
        (
            4,
            2,
            50.0,
        ),
        (
            4,
            1,
            75.0,
        ),
        (
            4,
            0,
            100.0,
        ),
    ),
)
def test_operational_percentage_accepts_consistent_unresolved_counts(
    enabled_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_count=enabled_count,
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_unresolved_count",
        "operational_percentage",
        "expected_message",
    ),
    (
        (
            0,
            0,
            25.0,
            (
                "analyst_operational_percentage must be zero "
                "when analyst_enabled_count is zero"
            ),
        ),
        (
            4,
            4,
            25.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_unresolved_count and "
                "analyst_enabled_count"
            ),
        ),
        (
            4,
            3,
            50.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_unresolved_count and "
                "analyst_enabled_count"
            ),
        ),
        (
            4,
            2,
            75.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_unresolved_count and "
                "analyst_enabled_count"
            ),
        ),
        (
            4,
            1,
            50.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_unresolved_count and "
                "analyst_enabled_count"
            ),
        ),
        (
            4,
            0,
            75.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_unresolved_count and "
                "analyst_enabled_count"
            ),
        ),
    ),
)
def test_operational_percentage_rejects_inconsistent_unresolved_counts(
    enabled_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            analyst_enabled_count=enabled_count,
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

def test_operational_percentage_allows_missing_unresolved_count_inputs(
) -> None:
    enabled_only = make_status(
        analyst_enabled_count=4,
        analyst_operational_percentage=75.0,
    )
    unresolved_only = make_status(
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75.0,
    )

    assert (
        enabled_only.analyst_operational_percentage
        == 75.0
    )
    assert (
        unresolved_only.analyst_operational_percentage
        == 75.0
    )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        25.0,
        50.0,
        75.0,
    ),
)
def test_zero_enabled_unresolved_count_rejects_partial_percentage(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be "
            "zero or 100 when "
            "analyst_enabled_unresolved_count is zero"
        ),
    ):
        make_status(
            analyst_enabled_unresolved_count=0,
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        100.0,
    ),
)
def test_zero_enabled_unresolved_count_allows_boundary_percentage(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_unresolved_count=0,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

def test_positive_enabled_unresolved_count_rejects_complete_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be "
            "less than 100 when "
            "analyst_enabled_unresolved_count is positive"
        ),
    ):
        make_status(
            analyst_enabled_unresolved_count=2,
            analyst_operational_percentage=100.0,
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        25.0,
        50.0,
        75.0,
    ),
)
def test_positive_enabled_unresolved_count_allows_incomplete_percentage(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_unresolved_count=2,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

def test_enabled_unresolved_count_allows_missing_operational_percentage(
) -> None:
    zero_unresolved = make_status(
        analyst_enabled_unresolved_count=0,
    )
    positive_unresolved = make_status(
        analyst_enabled_unresolved_count=2,
    )

    assert (
        zero_unresolved.analyst_operational_percentage
        is None
    )
    assert (
        positive_unresolved.analyst_operational_percentage
        is None
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_unresolved_count",
        "operational_status",
    ),
    (
        (
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            0,
            0,
            "DISABLED",
        ),
        (
            4,
            4,
            "UNRESOLVED",
        ),
        (
            4,
            3,
            "DEGRADED",
        ),
        (
            4,
            1,
            "DEGRADED",
        ),
        (
            4,
            0,
            "OPERATIONAL",
        ),
    ),
)
def test_operational_status_accepts_consistent_unresolved_counts(
    enabled_count: int,
    enabled_unresolved_count: int,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_count=enabled_count,
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_unresolved_count",
        "invalid_status",
        "expected_message",
    ),
    (
        (
            0,
            0,
            "UNRESOLVED",
            (
                "analyst_operational_status must be "
                "UNAVAILABLE or DISABLED when "
                "analyst_enabled_count is zero"
            ),
        ),
        (
            4,
            4,
            "DEGRADED",
            (
                "analyst_operational_status must agree "
                "with analyst_enabled_count and "
                "analyst_enabled_unresolved_count"
            ),
        ),
        (
            4,
            3,
            "UNRESOLVED",
            (
                "analyst_operational_status must agree "
                "with analyst_enabled_count and "
                "analyst_enabled_unresolved_count"
            ),
        ),
        (
            4,
            1,
            "OPERATIONAL",
            (
                "analyst_operational_status must be "
                "UNRESOLVED or DEGRADED when "
                "analyst_enabled_unresolved_count "
                "is positive"
            ),
        ),
        (
            4,
            0,
            "DEGRADED",
            (
                "analyst_operational_status must be "
                "UNAVAILABLE, DISABLED, or OPERATIONAL "
                "when analyst_enabled_unresolved_count "
                "is zero"
            ),
        ),
    ),
)
def test_operational_status_rejects_inconsistent_unresolved_counts(
    enabled_count: int,
    enabled_unresolved_count: int,
    invalid_status: str,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            analyst_enabled_count=enabled_count,
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_status=(
                invalid_status
            ),
        )

def test_operational_status_allows_missing_unresolved_count_inputs(
) -> None:
    enabled_only = make_status(
        analyst_enabled_count=4,
        analyst_operational_status="DEGRADED",
    )
    unresolved_only = make_status(
        analyst_enabled_unresolved_count=2,
        analyst_operational_status="DEGRADED",
    )

    assert (
        enabled_only.analyst_operational_status
        == "DEGRADED"
    )
    assert (
        unresolved_only.analyst_operational_status
        == "DEGRADED"
    )

@pytest.mark.parametrize(
    (
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
    ),
    (
        (
            0,
            0,
            0.0,
        ),
        (
            0,
            4,
            0.0,
        ),
        (
            1,
            3,
            25.0,
        ),
        (
            2,
            2,
            50.0,
        ),
        (
            3,
            1,
            75.0,
        ),
        (
            4,
            0,
            100.0,
        ),
    ),
)
def test_operational_percentage_accepts_consistent_component_counts(
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    (
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
        "expected_message",
    ),
    (
        (
            0,
            0,
            25.0,
            (
                "analyst_operational_percentage must be zero "
                "when analyst_enabled_resolved_count is zero"
            ),
        ),
        (
            0,
            4,
            25.0,
            (
                "analyst_operational_percentage must be zero "
                "when analyst_enabled_resolved_count is zero"
            ),
        ),
        (
            1,
            3,
            50.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_resolved_count and "
                "analyst_enabled_unresolved_count"
            ),
        ),
        (
            2,
            2,
            75.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_resolved_count and "
                "analyst_enabled_unresolved_count"
            ),
        ),
        (
            3,
            1,
            50.0,
            (
                "analyst_operational_percentage must agree "
                "with analyst_enabled_resolved_count and "
                "analyst_enabled_unresolved_count"
            ),
        ),
        (
            4,
            0,
            75.0,
            (
                "analyst_operational_percentage must be "
                "zero or 100 when "
                "analyst_enabled_unresolved_count is zero"
            ),
        ),
    ),
)
def test_operational_percentage_rejects_inconsistent_component_counts(
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        make_status(
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

def test_operational_percentage_allows_missing_component_count(
) -> None:
    resolved_only = make_status(
        analyst_enabled_resolved_count=3,
        analyst_operational_percentage=75.0,
    )
    unresolved_only = make_status(
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75.0,
    )

    assert (
        resolved_only.analyst_operational_percentage
        == 75.0
    )
    assert (
        unresolved_only.analyst_operational_percentage
        == 75.0
    )

@pytest.mark.parametrize(
    (
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_status",
    ),
    (
        (
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            0,
            0,
            "DISABLED",
        ),
        (
            0,
            4,
            "UNRESOLVED",
        ),
        (
            1,
            3,
            "DEGRADED",
        ),
        (
            3,
            1,
            "DEGRADED",
        ),
        (
            4,
            0,
            "OPERATIONAL",
        ),
    ),
)
def test_operational_status_accepts_consistent_component_counts(
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    (
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "invalid_status",
    ),
    (
        (
            0,
            0,
            "UNRESOLVED",
        ),
        (
            0,
            4,
            "DEGRADED",
        ),
        (
            1,
            3,
            "UNRESOLVED",
        ),
        (
            3,
            1,
            "OPERATIONAL",
        ),
        (
            4,
            0,
            "DEGRADED",
        ),
    ),
)
def test_operational_status_rejects_inconsistent_component_counts(
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    invalid_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_operational_status",
    ):
        make_status(
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_status=(
                invalid_status
            ),
        )

def test_operational_status_allows_missing_component_count(
) -> None:
    resolved_only = make_status(
        analyst_enabled_resolved_count=3,
        analyst_operational_status="DEGRADED",
    )
    unresolved_only = make_status(
        analyst_enabled_unresolved_count=1,
        analyst_operational_status="DEGRADED",
    )

    assert (
        resolved_only.analyst_operational_status
        == "DEGRADED"
    )
    assert (
        unresolved_only.analyst_operational_status
        == "DEGRADED"
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            0,
            0,
            0,
        ),
        (
            1,
            1,
            0,
        ),
        (
            1,
            0,
            1,
        ),
        (
            4,
            4,
            0,
        ),
        (
            4,
            3,
            1,
        ),
        (
            4,
            2,
            2,
        ),
        (
            4,
            0,
            4,
        ),
    ),
)
def test_enabled_count_accepts_consistent_component_counts(
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
) -> None:
    status = make_status(
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
    )

    assert status.analyst_enabled_count == enabled_count
    assert (
        status.analyst_enabled_resolved_count
        == enabled_resolved_count
    )
    assert (
        status.analyst_enabled_unresolved_count
        == enabled_unresolved_count
    )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            0,
            1,
            0,
        ),
        (
            0,
            0,
            1,
        ),
        (
            1,
            1,
            1,
        ),
        (
            4,
            2,
            1,
        ),
        (
            4,
            3,
            2,
        ),
        (
            4,
            0,
            3,
        ),
        (
            4,
            5,
            0,
        ),
    ),
)
def test_enabled_count_rejects_inconsistent_component_counts(
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_count|"
            "analyst_enabled_resolved_count|"
            "analyst_enabled_unresolved_count"
        ),
    ):
        make_status(
            analyst_enabled_count=enabled_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
        )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            4,
            3,
            None,
        ),
        (
            4,
            None,
            1,
        ),
        (
            None,
            3,
            1,
        ),
        (
            4,
            None,
            None,
        ),
        (
            None,
            3,
            None,
        ),
        (
            None,
            None,
            1,
        ),
    ),
)
def test_enabled_count_composition_allows_missing_count(
    enabled_count: int | None,
    enabled_resolved_count: int | None,
    enabled_unresolved_count: int | None,
) -> None:
    status = make_status(
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
    )

    assert status.analyst_enabled_count == enabled_count
    assert (
        status.analyst_enabled_resolved_count
        == enabled_resolved_count
    )
    assert (
        status.analyst_enabled_unresolved_count
        == enabled_unresolved_count
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            0,
            0,
            0,
        ),
        (
            1,
            1,
            0,
        ),
        (
            1,
            0,
            1,
        ),
        (
            4,
            2,
            1,
        ),
        (
            4,
            3,
            1,
        ),
        (
            10,
            4,
            2,
        ),
    ),
)
def test_domain_count_accepts_enabled_component_total(
    domain_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
    )

    assert status.analyst_domain_count == domain_count
    assert (
        status.analyst_enabled_resolved_count
        == enabled_resolved_count
    )
    assert (
        status.analyst_enabled_unresolved_count
        == enabled_unresolved_count
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            0,
            1,
            0,
        ),
        (
            0,
            0,
            1,
        ),
        (
            1,
            1,
            1,
        ),
        (
            4,
            3,
            2,
        ),
        (
            4,
            5,
            0,
        ),
        (
            4,
            0,
            5,
        ),
    ),
)
def test_domain_count_rejects_excess_enabled_component_total(
    domain_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_domain_count|"
            "analyst_enabled_resolved_count|"
            "analyst_enabled_unresolved_count"
        ),
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
        )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
    ),
    (
        (
            4,
            3,
            None,
        ),
        (
            4,
            None,
            1,
        ),
        (
            None,
            3,
            1,
        ),
        (
            4,
            None,
            None,
        ),
    ),
)
def test_domain_component_validation_allows_missing_count(
    domain_count: int | None,
    enabled_resolved_count: int | None,
    enabled_unresolved_count: int | None,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
    )

    assert status.analyst_domain_count == domain_count
    assert (
        status.analyst_enabled_resolved_count
        == enabled_resolved_count
    )
    assert (
        status.analyst_enabled_unresolved_count
        == enabled_unresolved_count
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_status",
    ),
    (
        (
            0,
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            0,
            0,
            "DISABLED",
        ),
        (
            4,
            0,
            4,
            "UNRESOLVED",
        ),
        (
            4,
            1,
            3,
            "DEGRADED",
        ),
        (
            4,
            3,
            1,
            "DEGRADED",
        ),
        (
            4,
            4,
            0,
            "OPERATIONAL",
        ),
    ),
)
def test_operational_status_accepts_consistent_domain_component_counts(
    domain_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "invalid_status",
    ),
    (
        (
            0,
            0,
            0,
            "DISABLED",
        ),
        (
            4,
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            0,
            4,
            "DEGRADED",
        ),
        (
            4,
            1,
            3,
            "UNRESOLVED",
        ),
        (
            4,
            3,
            1,
            "OPERATIONAL",
        ),
        (
            4,
            4,
            0,
            "DEGRADED",
        ),
    ),
)
def test_operational_status_rejects_inconsistent_domain_component_counts(
    domain_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    invalid_status: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="analyst_operational_status",
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_status=(
                invalid_status
            ),
        )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_status",
    ),
    (
        (
            None,
            0,
            0,
            "UNAVAILABLE",
        ),
        (
            4,
            None,
            0,
            "DISABLED",
        ),
        (
            4,
            0,
            None,
            "DISABLED",
        ),
        (
            None,
            1,
            1,
            "DEGRADED",
        ),
    ),
)
def test_domain_component_status_validation_allows_missing_count(
    domain_count: int | None,
    enabled_resolved_count: int | None,
    enabled_unresolved_count: int | None,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert (
        status.analyst_operational_status
        == operational_status
    )

def test_zero_domain_count_allows_zero_operational_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_operational_percentage=0.0,
    )

    assert status.analyst_domain_count == 0
    assert status.analyst_operational_percentage == 0.0

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0001,
        25.0,
        50.0,
        75.0,
        100.0,
    ),
)
def test_zero_domain_count_rejects_positive_operational_percentage(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be zero "
            "when analyst_domain_count is zero"
        ),
    ):
        make_status(
            analyst_domain_count=0,
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        1e-7,
        5e-7,
        1e-6,
    ),
)
def test_zero_domain_count_accepts_effectively_zero_percentage(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_domain_count=0,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        25.0,
        50.0,
        75.0,
        100.0,
    ),
)
def test_positive_domain_count_allows_partial_operational_percentage(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert status.analyst_domain_count == 4
    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "domain_count",
    (
        0,
        1,
        4,
    ),
)
def test_domain_count_allows_missing_operational_percentage(
    domain_count: int,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
    )

    assert status.analyst_domain_count == domain_count
    assert status.analyst_operational_percentage is None

@pytest.mark.parametrize(
    "operational_status",
    (
        "DISABLED",
        "UNRESOLVED",
        "DEGRADED",
        "OPERATIONAL",
    ),
)
def test_positive_domain_count_allows_available_operational_status(
    operational_status: str,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_operational_status=operational_status,
    )

    assert status.analyst_domain_count == 4
    assert (
        status.analyst_operational_status
        == operational_status
    )

def test_positive_domain_count_rejects_unavailable_operational_status(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_status must not be "
            "UNAVAILABLE when analyst_domain_count is positive"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_operational_status="UNAVAILABLE",
        )

def test_operational_status_allows_missing_domain_count(
) -> None:
    unavailable = make_status(
        analyst_operational_status="UNAVAILABLE",
    )
    operational = make_status(
        analyst_operational_status="OPERATIONAL",
    )

    assert (
        unavailable.analyst_operational_status
        == "UNAVAILABLE"
    )
    assert (
        operational.analyst_operational_status
        == "OPERATIONAL"
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
        "operational_status",
    ),
    (
        (
            0,
            0,
            0,
            0,
            0.0,
            "UNAVAILABLE",
        ),
        (
            4,
            0,
            0,
            0,
            0.0,
            "DISABLED",
        ),
        (
            4,
            4,
            0,
            4,
            0.0,
            "UNRESOLVED",
        ),
        (
            4,
            4,
            1,
            3,
            25.0,
            "DEGRADED",
        ),
        (
            4,
            4,
            2,
            2,
            50.0,
            "DEGRADED",
        ),
        (
            4,
            4,
            3,
            1,
            75.0,
            "DEGRADED",
        ),
        (
            4,
            4,
            4,
            0,
            100.0,
            "OPERATIONAL",
        ),
        (
            10,
            4,
            2,
            2,
            50.0,
            "DEGRADED",
        ),
        (
            10,
            4,
            4,
            0,
            100.0,
            "OPERATIONAL",
        ),
    ),
)
def test_complete_operational_payload_accepts_consistent_state(
    domain_count: int,
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
    operational_status: str,
) -> None:
    status = make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

    assert status.analyst_domain_count == domain_count
    assert status.analyst_enabled_count == enabled_count
    assert (
        status.analyst_enabled_resolved_count
        == enabled_resolved_count
    )
    assert (
        status.analyst_enabled_unresolved_count
        == enabled_unresolved_count
    )
    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )
    assert (
        status.analyst_operational_status
        == operational_status
    )

@pytest.mark.parametrize(
    (
        "domain_count",
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
        "operational_status",
    ),
    (
        # Zero domains cannot be disabled.
        (
            0,
            0,
            0,
            0,
            0.0,
            "DISABLED",
        ),
        # Positive domains with no enabled analysts are disabled.
        (
            4,
            0,
            0,
            0,
            0.0,
            "UNAVAILABLE",
        ),
        # Enabled count must equal resolved plus unresolved.
        (
            4,
            4,
            2,
            1,
            50.0,
            "DEGRADED",
        ),
        # Percentage must agree with component counts.
        (
            4,
            4,
            1,
            3,
            50.0,
            "DEGRADED",
        ),
        # Status must agree with unresolved state.
        (
            4,
            4,
            0,
            4,
            0.0,
            "DEGRADED",
        ),
        # Partial resolution cannot be operational.
        (
            4,
            4,
            3,
            1,
            75.0,
            "OPERATIONAL",
        ),
        # Complete resolution requires 100%.
        (
            4,
            4,
            4,
            0,
            75.0,
            "OPERATIONAL",
        ),
        # Complete resolution requires operational status.
        (
            4,
            4,
            4,
            0,
            100.0,
            "DEGRADED",
        ),
        # Enabled analysts cannot exceed domains.
        (
            4,
            5,
            5,
            0,
            100.0,
            "OPERATIONAL",
        ),
        # Component total cannot exceed domains.
        (
            4,
            5,
            3,
            2,
            60.0,
            "DEGRADED",
        ),
    ),
)
def test_complete_operational_payload_rejects_inconsistent_state(
    domain_count: int,
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
    operational_status: str,
) -> None:
    with pytest.raises(ValueError):
        make_status(
            analyst_domain_count=domain_count,
            analyst_enabled_count=enabled_count,
            analyst_enabled_resolved_count=(
                enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                enabled_unresolved_count
            ),
            analyst_operational_percentage=(
                operational_percentage
            ),
            analyst_operational_status=(
                operational_status
            ),
        )

def make_complete_operational_status(
    *,
    domain_count: int,
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
    operational_status: str,
):
    return make_status(
        analyst_domain_count=domain_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
        analyst_operational_status=(
            operational_status
        ),
    )

@pytest.mark.parametrize(
    "payload",
    (
        {
            "domain_count": 0,
            "enabled_count": 0,
            "enabled_resolved_count": 0,
            "enabled_unresolved_count": 0,
            "operational_percentage": 0.0,
            "operational_status": "UNAVAILABLE",
        },
        {
            "domain_count": 4,
            "enabled_count": 0,
            "enabled_resolved_count": 0,
            "enabled_unresolved_count": 0,
            "operational_percentage": 0.0,
            "operational_status": "DISABLED",
        },
        {
            "domain_count": 4,
            "enabled_count": 4,
            "enabled_resolved_count": 0,
            "enabled_unresolved_count": 4,
            "operational_percentage": 0.0,
            "operational_status": "UNRESOLVED",
        },
        {
            "domain_count": 4,
            "enabled_count": 4,
            "enabled_resolved_count": 2,
            "enabled_unresolved_count": 2,
            "operational_percentage": 50.0,
            "operational_status": "DEGRADED",
        },
        {
            "domain_count": 4,
            "enabled_count": 4,
            "enabled_resolved_count": 4,
            "enabled_unresolved_count": 0,
            "operational_percentage": 100.0,
            "operational_status": "OPERATIONAL",
        },
    ),
)
def test_complete_operational_baselines_are_valid(
    payload: dict[str, int | float | str],
) -> None:
    status = make_complete_operational_status(
        **payload,
    )

    assert (
        status.analyst_operational_status
        == payload["operational_status"]
    )
    assert (
        status.analyst_operational_percentage
        == payload["operational_percentage"]
    )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    (
        (
            "domain_count",
            1,
        ),
        (
            "enabled_count",
            1,
        ),
        (
            "enabled_resolved_count",
            1,
        ),
        (
            "enabled_unresolved_count",
            1,
        ),
        (
            "operational_percentage",
            25.0,
        ),
        (
            "operational_status",
            "DISABLED",
        ),
    ),
)
def test_unavailable_state_rejects_single_field_mutation(
    field_name: str,
    invalid_value: float | str,
) -> None:
    payload = {
        "domain_count": 0,
        "enabled_count": 0,
        "enabled_resolved_count": 0,
        "enabled_unresolved_count": 0,
        "operational_percentage": 0.0,
        "operational_status": "UNAVAILABLE",
    }

    payload[field_name] = invalid_value

    with pytest.raises(ValueError):
        make_complete_operational_status(
            **payload,
        )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    (
        (
            "domain_count",
            0,
        ),
        (
            "enabled_count",
            1,
        ),
        (
            "enabled_resolved_count",
            1,
        ),
        (
            "enabled_unresolved_count",
            1,
        ),
        (
            "operational_percentage",
            25.0,
        ),
        (
            "operational_status",
            "UNAVAILABLE",
        ),
    ),
)
def test_disabled_state_rejects_single_field_mutation(
    field_name: str,
    invalid_value: float | str,
) -> None:
    payload = {
        "domain_count": 4,
        "enabled_count": 0,
        "enabled_resolved_count": 0,
        "enabled_unresolved_count": 0,
        "operational_percentage": 0.0,
        "operational_status": "DISABLED",
    }

    payload[field_name] = invalid_value

    with pytest.raises(ValueError):
        make_complete_operational_status(
            **payload,
        )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    (
        (
            "domain_count",
            3,
        ),
        (
            "enabled_count",
            3,
        ),
        (
            "enabled_resolved_count",
            1,
        ),
        (
            "enabled_unresolved_count",
            3,
        ),
        (
            "operational_percentage",
            25.0,
        ),
        (
            "operational_status",
            "DEGRADED",
        ),
    ),
)
def test_unresolved_state_rejects_single_field_mutation(
    field_name: str,
    invalid_value: float | str,
) -> None:
    payload = {
        "domain_count": 4,
        "enabled_count": 4,
        "enabled_resolved_count": 0,
        "enabled_unresolved_count": 4,
        "operational_percentage": 0.0,
        "operational_status": "UNRESOLVED",
    }

    payload[field_name] = invalid_value

    with pytest.raises(ValueError):
        make_complete_operational_status(
            **payload,
        )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    (
        (
            "domain_count",
            3,
        ),
        (
            "enabled_count",
            3,
        ),
        (
            "enabled_resolved_count",
            3,
        ),
        (
            "enabled_unresolved_count",
            1,
        ),
        (
            "operational_percentage",
            75.0,
        ),
        (
            "operational_status",
            "OPERATIONAL",
        ),
    ),
)
def test_degraded_state_rejects_single_field_mutation(
    field_name: str,
    invalid_value: float | str,
) -> None:
    payload = {
        "domain_count": 4,
        "enabled_count": 4,
        "enabled_resolved_count": 2,
        "enabled_unresolved_count": 2,
        "operational_percentage": 50.0,
        "operational_status": "DEGRADED",
    }

    payload[field_name] = invalid_value

    with pytest.raises(ValueError):
        make_complete_operational_status(
            **payload,
        )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    (
        (
            "domain_count",
            3,
        ),
        (
            "enabled_count",
            3,
        ),
        (
            "enabled_resolved_count",
            3,
        ),
        (
            "enabled_unresolved_count",
            1,
        ),
        (
            "operational_percentage",
            75.0,
        ),
        (
            "operational_status",
            "DEGRADED",
        ),
    ),
)
def test_operational_state_rejects_single_field_mutation(
    field_name: str,
    invalid_value: float | str,
) -> None:
    payload = {
        "domain_count": 4,
        "enabled_count": 4,
        "enabled_resolved_count": 4,
        "enabled_unresolved_count": 0,
        "operational_percentage": 100.0,
        "operational_status": "OPERATIONAL",
    }

    payload[field_name] = invalid_value

    with pytest.raises(ValueError):
        make_complete_operational_status(
            **payload,
        )

@pytest.mark.parametrize(
    (
        "enabled_count",
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
    ),
    (
        (
            3,
            1,
            2,
            (1 / 3) * 100.0,
        ),
        (
            3,
            2,
            1,
            (2 / 3) * 100.0,
        ),
        (
            6,
            1,
            5,
            (1 / 6) * 100.0,
        ),
        (
            6,
            5,
            1,
            (5 / 6) * 100.0,
        ),
        (
            7,
            2,
            5,
            (2 / 7) * 100.0,
        ),
        (
            7,
            5,
            2,
            (5 / 7) * 100.0,
        ),
    ),
)
def test_operational_percentage_accepts_repeating_count_ratios(
    enabled_count: int,
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_domain_count=enabled_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
        analyst_operational_status="DEGRADED",
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "percentage_adjustment",
    (
        -1e-7,
        1e-7,
        -5e-7,
        5e-7,
        -1e-6,
        1e-6,
    ),
)
def test_operational_percentage_accepts_repeating_ratio_within_tolerance(
    percentage_adjustment: float,
) -> None:
    expected_percentage = (1 / 3) * 100.0
    supplied_percentage = (
        expected_percentage
        + percentage_adjustment
    )

    status = make_status(
        analyst_domain_count=3,
        analyst_enabled_count=3,
        analyst_enabled_resolved_count=1,
        analyst_enabled_unresolved_count=2,
        analyst_operational_percentage=(
            supplied_percentage
        ),
        analyst_operational_status="DEGRADED",
    )

    assert (
        status.analyst_operational_percentage
        == supplied_percentage
    )

@pytest.mark.parametrize(
    "percentage_adjustment",
    (
        -0.0001,
        0.0001,
        -0.01,
        0.01,
        -1.0,
        1.0,
    ),
)
def test_operational_percentage_rejects_repeating_ratio_outside_tolerance(
    percentage_adjustment: float,
) -> None:
    expected_percentage = (1 / 3) * 100.0
    supplied_percentage = (
        expected_percentage
        + percentage_adjustment
    )

    with pytest.raises(
        ValueError,
        match="analyst_operational_percentage",
    ):
        make_status(
            analyst_domain_count=3,
            analyst_enabled_count=3,
            analyst_enabled_resolved_count=1,
            analyst_enabled_unresolved_count=2,
            analyst_operational_percentage=(
                supplied_percentage
            ),
            analyst_operational_status="DEGRADED",
        )

@pytest.mark.parametrize(
    (
        "enabled_resolved_count",
        "enabled_unresolved_count",
        "operational_percentage",
    ),
    (
        (
            1,
            2,
            (1 / 3) * 100.0,
        ),
        (
            2,
            1,
            (2 / 3) * 100.0,
        ),
        (
            1,
            6,
            (1 / 7) * 100.0,
        ),
        (
            6,
            1,
            (6 / 7) * 100.0,
        ),
    ),
)
def test_operational_percentage_accepts_repeating_component_ratio_without_enabled_count(
    enabled_resolved_count: int,
    enabled_unresolved_count: int,
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_enabled_resolved_count=(
            enabled_resolved_count
        ),
        analyst_enabled_unresolved_count=(
            enabled_unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
        analyst_operational_status="DEGRADED",
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_operational_percentage_rejects_non_finite_values(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be finite"
        ),
    ):
        make_status(
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_complete_operational_payload_rejects_non_finite_percentage(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be finite"
        ),
    ):
        make_status(
            analyst_domain_count=4,
            analyst_enabled_count=4,
            analyst_enabled_resolved_count=2,
            analyst_enabled_unresolved_count=2,
            analyst_operational_percentage=(
                operational_percentage
            ),
            analyst_operational_status="DEGRADED",
        )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        0.0,
        25.0,
        50.0,
        75.0,
        100.0,
    ),
)
def test_operational_percentage_accepts_finite_values(
    operational_percentage: float,
) -> None:
    status = make_status(
        analyst_operational_percentage=(
            operational_percentage
        ),
    )

    assert (
        status.analyst_operational_percentage
        == operational_percentage
    )

@pytest.mark.parametrize(
    "field_name",
    (
        "institutional_bias_confidence",
        "institutional_bias_strength",
        "institutional_bias_bullish_score",
        "institutional_bias_bearish_score",
        "market_phase_confidence",
        "market_phase_strength",
        "confluence_score",
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
    ),
)
@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_normalized_confidence_fields_reject_non_finite_values(
    field_name: str,
    non_finite_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=rf"{field_name} must be finite",
    ):
        make_status(
            **{
                field_name: non_finite_value,
            },
        )

@pytest.mark.parametrize(
    "field_name",
    (
        "institutional_bias_confidence",
        "institutional_bias_strength",
        "institutional_bias_bullish_score",
        "institutional_bias_bearish_score",
        "market_phase_confidence",
        "market_phase_strength",
        "confluence_score",
        "trend_confidence",
        "structure_confidence",
        "liquidity_confidence",
        "order_block_confidence",
        "auction_confidence",
        "pressure_confidence",
        "participation_confidence",
        "value_confidence",
        "acceptance_confidence",
        "analyst_average_confidence",
        "analyst_enabled_average_confidence",
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
@pytest.mark.parametrize(
    "finite_value",
    (
        0.0,
        50.0,
        100.0,
    ),
)
def test_normalized_confidence_fields_accept_finite_boundaries(
    field_name: str,
    finite_value: float,
) -> None:
    status = make_status(
        **{
            field_name: finite_value,
        },
    )

    assert getattr(
        status,
        field_name,
    ) == finite_value

@pytest.mark.parametrize(
    "field_name",
    (
        "institutional_bias_confidence",
        "institutional_bias_strength",
        "institutional_bias_bullish_score",
        "institutional_bias_bearish_score",
        "market_phase_confidence",
        "market_phase_strength",
        "confluence_score",
        "trend_confidence",
        "structure_confidence",
        "liquidity_confidence",
        "order_block_confidence",
        "auction_confidence",
        "pressure_confidence",
        "participation_confidence",
        "value_confidence",
        "analyst_average_confidence",
        "acceptance_confidence",
        "analyst_enabled_average_confidence",
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_normalized_confidence_fields_accept_finite_zero(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: 0.0,
        },
    )

    assert getattr(
        status,
        field_name,
    ) == 0.0

@pytest.mark.parametrize(
    (
        "supplied_value",
        "expected_value",
    ),
    (
        (
            0,
            0.0,
        ),
        (
            25,
            25.0,
        ),
        (
            50.5,
            50.5,
        ),
        (
            100,
            100.0,
        ),
    ),
)
def test_acceptance_confidence_normalizes_finite_numeric_values(
    supplied_value: float,
    expected_value: float,
) -> None:
    status = make_status(
        acceptance_confidence=supplied_value,
    )

    assert (
        status.acceptance_confidence
        == expected_value
    )
    assert isinstance(
        status.acceptance_confidence,
        float,
    )

@pytest.mark.parametrize(
    "invalid_value",
    (
        True,
        False,
        "50",
        object(),
    ),
)
def test_acceptance_confidence_rejects_non_numeric_values(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "acceptance_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            acceptance_confidence=invalid_value,
        )

@pytest.mark.parametrize(
    "invalid_value",
    (
        -0.0001,
        -1.0,
        100.0001,
        101.0,
    ),
)
def test_acceptance_confidence_rejects_out_of_range_values(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "acceptance_confidence must be "
            "between 0 and 100"
        ),
    ):
        make_status(
            acceptance_confidence=invalid_value,
        )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "boolean_value",
    (
        False,
        True,
    ),
)
def test_normalized_confidence_fields_reject_boolean_values(
    field_name: str,
    boolean_value: bool,
) -> None:
    with pytest.raises(
        TypeError,
        match=rf"{field_name} must be a number or None",
    ):
        make_status(
            **{
                field_name: boolean_value,
            },
        )

@pytest.mark.parametrize(
    "boolean_value",
    (
        False,
        True,
    ),
)
def test_acceptance_confidence_rejects_boolean_values(
    boolean_value: bool,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "acceptance_confidence must be "
            "a number or None"
        ),
    ):
        make_status(
            acceptance_confidence=boolean_value,
        )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "50",
        "",
        [],
        {},
        object(),
    ),
)
def test_normalized_confidence_fields_reject_non_numeric_values(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=rf"{field_name} must be a number or None",
    ):
        make_status(
            **{
                field_name: invalid_value,
            },
        )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
def test_normalized_confidence_fields_allow_none(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: None,
        },
    )

    assert getattr(
        status,
        field_name,
    ) is None

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        -100.0,
        -1.0,
        -0.0001,
        100.0001,
        101.0,
        200.0,
    ),
)
def test_normalized_confidence_fields_reject_out_of_range_values(
    field_name: str,
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=rf"{field_name} must be between 0 and 100",
    ):
        make_status(
            **{
                field_name: invalid_value,
            },
        )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "boundary_value",
    (
        0,
        100,
    ),
)
def test_normalized_confidence_fields_accept_range_boundaries(
    field_name: str,
    boundary_value: float,
) -> None:
    status = make_status(
        **{
            field_name: boundary_value,
        },
    )

    assert getattr(
        status,
        field_name,
    ) == float(boundary_value)

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "boundary_value",
    (
        0,
        100,
    ),
)
def test_core_confidence_fields_accept_range_boundaries(
    field_name: str,
    boundary_value: float,
) -> None:
    status = make_status(
        **{
            field_name: boundary_value,
        },
    )

    assert getattr(
        status,
        field_name,
    ) == float(boundary_value)

@pytest.mark.parametrize(
    "field_name",
    (
        "analyst_average_confidence",
        "analyst_enabled_average_confidence",
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_analyst_confidence_fields_accept_zero_boundary(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: 0,
        },
    )

    assert getattr(
        status,
        field_name,
    ) == 0.0

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "integer_value",
    (
        0,
        25,
        50,
        75,
        100,
    ),
)
def test_normalized_confidence_fields_convert_integers_to_float(
    field_name: str,
    integer_value: int,
) -> None:
    status = make_status(
        **{
            field_name: integer_value,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == float(integer_value)
    assert isinstance(
        stored_value,
        float,
    )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "integer_value",
    (
        0,
        25,
        50,
        75,
        100,
    ),
)
def test_core_confidence_fields_convert_integers_to_float(
    field_name: str,
    integer_value: int,
) -> None:
    status = make_status(
        **{
            field_name: integer_value,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == float(integer_value)
    assert isinstance(
        stored_value,
        float,
    )

@pytest.mark.parametrize(
    "field_name",
    (
        "analyst_average_confidence",
        "analyst_enabled_average_confidence",
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_analyst_confidence_fields_convert_zero_integer_to_float(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: 0,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == 0.0
    assert isinstance(
        stored_value,
        float,
    )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
@pytest.mark.parametrize(
    "float_value",
    (
        0.5,
        25.25,
        50.5,
        75.75,
        99.999,
    ),
)
def test_core_confidence_fields_preserve_float_values(
    field_name: str,
    float_value: float,
) -> None:
    status = make_status(
        **{
            field_name: float_value,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == float_value
    assert isinstance(
        stored_value,
        float,
    )

@pytest.mark.parametrize(
    (
        "field_name",
        "supplied_value",
        "expected_value",
    ),
    (
        (
            "institutional_bias_confidence",
            75,
            75.0,
        ),
        (
            "market_phase_confidence",
            50,
            50.0,
        ),
        (
            "confluence_score",
            25,
            25.0,
        ),
        (
            "acceptance_confidence",
            80,
            80.0,
        ),
        (
            "trend_confidence",
            60,
            60.0,
        ),
        (
            "structure_confidence",
            70,
            70.0,
        ),
        (
            "liquidity_confidence",
            65,
            65.0,
        ),
        (
            "analyst_average_confidence",
            0,
            0.0,
        ),
        (
            "analyst_enabled_average_confidence",
            0,
            0.0,
        ),
        (
            "analyst_confidence_coverage_percentage",
            0,
            0.0,
        ),
        (
            "analyst_enabled_confidence_coverage_percentage",
            0,
            0.0,
        ),
        (
            "analyst_coverage_percentage",
            0,
            0.0,
        ),
        (
            "analyst_operational_percentage",
            0,
            0.0,
        ),
    ),
)
def test_to_dict_preserves_normalized_numeric_fields(
    field_name: str,
    supplied_value: int,
    expected_value: float,
) -> None:
    status = make_status(
        **{
            field_name: supplied_value,
        },
    )

    payload = status.to_dict()

    assert payload[field_name] == expected_value
    assert isinstance(
        payload[field_name],
        float,
    )

@pytest.mark.parametrize(
    (
        "field_name",
        "supplied_value",
    ),
    (
        (
            "institutional_bias_confidence",
            75.25,
        ),
        (
            "market_phase_confidence",
            50.5,
        ),
        (
            "confluence_score",
            25.75,
        ),
        (
            "acceptance_confidence",
            80.125,
        ),
        (
            "trend_confidence",
            60.625,
        ),
        (
            "structure_confidence",
            70.875,
        ),
        (
            "liquidity_confidence",
            65.375,
        ),
    ),
)
def test_to_dict_preserves_normalized_decimal_values(
    field_name: str,
    supplied_value: float,
) -> None:
    status = make_status(
        **{
            field_name: supplied_value,
        },
    )

    payload = status.to_dict()

    assert payload[field_name] == supplied_value
    assert isinstance(
        payload[field_name],
        float,
    )

@pytest.mark.parametrize(
    "field_name",
    (
        "institutional_bias_confidence",
        "market_phase_confidence",
        "confluence_score",
        "acceptance_confidence",
        "trend_confidence",
        "structure_confidence",
        "liquidity_confidence",
        "analyst_average_confidence",
        "analyst_enabled_average_confidence",
        "analyst_confidence_coverage_percentage",
        "analyst_enabled_confidence_coverage_percentage",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_to_dict_preserves_none_normalized_fields(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: None,
        },
    )

    payload = status.to_dict()

    assert payload[field_name] is None


def test_to_json_serializes_normalized_operational_percentage(
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    payload = json.loads(
        status.to_json()
    )

    assert (
        payload["analyst_operational_percentage"]
        == 75.0
    )
    assert isinstance(
        payload["analyst_operational_percentage"],
        float,
    )

@pytest.mark.parametrize(
    "operational_percentage",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_non_finite_operational_percentage_is_rejected_before_json(
    operational_percentage: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_operational_percentage must be finite"
        ),
    ):
        status = make_status(
            analyst_operational_percentage=(
                operational_percentage
            ),
        )

        status.to_json()

def test_to_dict_serializes_complete_normalized_payload(
) -> None:
    status = make_status(
        institutional_bias_confidence=81,
        institutional_bias_strength=72,
        institutional_bias_bullish_score=68,
        institutional_bias_bearish_score=32,
        market_phase_confidence=76,
        market_phase_strength=64,
        confluence_score=79,
        acceptance_confidence=74,
        trend_confidence=82,
        structure_confidence=71,
        liquidity_confidence=69,
        order_block_confidence=66,
        auction_confidence=73,
        pressure_confidence=77,
        participation_confidence=63,
        value_confidence=70,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_average_confidence=75,
        analyst_enabled_average_confidence=75,
        analyst_confidence_coverage_percentage=100,
        analyst_enabled_confidence_coverage_percentage=100,
        analyst_coverage_percentage=100,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    payload = status.to_dict()

    expected_values = {
        "institutional_bias_confidence": 81.0,
        "institutional_bias_strength": 72.0,
        "institutional_bias_bullish_score": 68.0,
        "institutional_bias_bearish_score": 32.0,
        "market_phase_confidence": 76.0,
        "market_phase_strength": 64.0,
        "confluence_score": 79.0,
        "acceptance_confidence": 74.0,
        "trend_confidence": 82.0,
        "structure_confidence": 71.0,
        "liquidity_confidence": 69.0,
        "order_block_confidence": 66.0,
        "auction_confidence": 73.0,
        "pressure_confidence": 77.0,
        "participation_confidence": 63.0,
        "value_confidence": 70.0,
        "analyst_average_confidence": 75.0,
        "analyst_enabled_average_confidence": 75.0,
        "analyst_confidence_coverage_percentage": 100.0,
        "analyst_enabled_confidence_coverage_percentage": 100.0,
        "analyst_coverage_percentage": 100.0,
        "analyst_operational_percentage": 75.0,
    }

    for field_name, expected_value in (
        expected_values.items()
    ):
        assert payload[field_name] == expected_value
        assert isinstance(
            payload[field_name],
            float,
        )

    assert payload["analyst_domain_count"] == 4
    assert payload["analyst_enabled_count"] == 4
    assert (
        payload["analyst_enabled_resolved_count"]
        == 3
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 1
    )
    assert (
        payload["analyst_operational_status"]
        == "DEGRADED"
    )

def test_to_json_serializes_complete_normalized_payload(
) -> None:
    status = make_status(
        institutional_bias_confidence=81,
        institutional_bias_strength=72,
        institutional_bias_bullish_score=68,
        institutional_bias_bearish_score=32,
        market_phase_confidence=76,
        market_phase_strength=64,
        confluence_score=79,
        acceptance_confidence=74,
        trend_confidence=82,
        structure_confidence=71,
        liquidity_confidence=69,
        order_block_confidence=66,
        auction_confidence=73,
        pressure_confidence=77,
        participation_confidence=63,
        value_confidence=70,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_average_confidence=75,
        analyst_enabled_average_confidence=75,
        analyst_confidence_coverage_percentage=100,
        analyst_enabled_confidence_coverage_percentage=100,
        analyst_coverage_percentage=100,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    payload = json.loads(
        status.to_json()
    )

    normalized_field_names = (
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
    )

    for field_name in normalized_field_names:
        assert isinstance(
            payload[field_name],
            float,
        )

    assert (
        payload["analyst_operational_percentage"]
        == 75.0
    )
    assert (
        payload["analyst_operational_status"]
        == "DEGRADED"
    )

def test_serialization_does_not_mutate_normalized_fields(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    before = (
        status.trend_confidence,
        status.acceptance_confidence,
        status.analyst_operational_percentage,
    )

    status.to_dict()
    status.to_json()

    after = (
        status.trend_confidence,
        status.acceptance_confidence,
        status.analyst_operational_percentage,
    )

    assert after == before
    assert all(
        isinstance(value, float)
        for value in after
    )

def test_complete_payload_json_matches_dictionary_serialization(
) -> None:
    status = make_status(
        institutional_bias_confidence=81,
        institutional_bias_strength=72,
        institutional_bias_bullish_score=68,
        institutional_bias_bearish_score=32,
        market_phase_confidence=76,
        market_phase_strength=64,
        confluence_score=79,
        acceptance_confidence=74,
        trend_confidence=82,
        structure_confidence=71,
        liquidity_confidence=69,
        order_block_confidence=66,
        auction_confidence=73,
        pressure_confidence=77,
        participation_confidence=63,
        value_confidence=70,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_average_confidence=75,
        analyst_enabled_average_confidence=75,
        analyst_confidence_coverage_percentage=100,
        analyst_enabled_confidence_coverage_percentage=100,
        analyst_coverage_percentage=100,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    dictionary_payload = status.to_dict()
    json_payload = json.loads(
        status.to_json()
    )

    assert json_payload == dictionary_payload

def test_partial_payload_json_matches_dictionary_serialization(
) -> None:
    status = make_status(
        trend_confidence=82,
        acceptance_confidence=74,
        analyst_domain_count=4,
        analyst_operational_status="DEGRADED",
    )

    dictionary_payload = status.to_dict()
    json_payload = json.loads(
        status.to_json()
    )

    assert json_payload == dictionary_payload

def test_missing_operational_fields_match_across_serializers(
) -> None:
    status = make_status()

    dictionary_payload = status.to_dict()
    json_payload = json.loads(
        status.to_json()
    )

    assert json_payload == dictionary_payload
    assert (
        json_payload["analyst_operational_status"]
        is None
    )
    assert (
        json_payload["analyst_operational_percentage"]
        is None
    )

@pytest.mark.parametrize(
    (
        "resolved_count",
        "unresolved_count",
        "operational_percentage",
    ),
    (
        (
            1,
            2,
            (1 / 3) * 100.0,
        ),
        (
            2,
            1,
            (2 / 3) * 100.0,
        ),
        (
            1,
            6,
            (1 / 7) * 100.0,
        ),
        (
            6,
            1,
            (6 / 7) * 100.0,
        ),
    ),
)
def test_repeating_operational_percentage_matches_across_serializers(
    resolved_count: int,
    unresolved_count: int,
    operational_percentage: float,
) -> None:
    enabled_count = (
        resolved_count
        + unresolved_count
    )

    status = make_status(
        analyst_domain_count=enabled_count,
        analyst_enabled_count=enabled_count,
        analyst_enabled_resolved_count=(
            resolved_count
        ),
        analyst_enabled_unresolved_count=(
            unresolved_count
        ),
        analyst_operational_percentage=(
            operational_percentage
        ),
        analyst_operational_status="DEGRADED",
    )

    dictionary_payload = status.to_dict()
    json_payload = json.loads(
        status.to_json()
    )

    assert json_payload == dictionary_payload
    assert (
        json_payload["analyst_operational_percentage"]
        == operational_percentage
    )

def test_repeated_serialization_returns_equivalent_payloads(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    first_dictionary_payload = status.to_dict()
    second_dictionary_payload = status.to_dict()

    first_json_payload = json.loads(
        status.to_json()
    )
    second_json_payload = json.loads(
        status.to_json()
    )

    assert (
        first_dictionary_payload
        == second_dictionary_payload
    )
    assert (
        first_json_payload
        == second_json_payload
    )
    assert (
        first_json_payload
        == first_dictionary_payload
    )

def test_mutating_dictionary_payload_does_not_change_status(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    payload = status.to_dict()

    payload["trend_confidence"] = 10.0
    payload["acceptance_confidence"] = 20.0
    payload["analyst_operational_percentage"] = 100.0
    payload["analyst_operational_status"] = "OPERATIONAL"

    assert status.trend_confidence == 75.0
    assert status.acceptance_confidence == 80.0
    assert (
        status.analyst_operational_percentage
        == 75.0
    )
    assert (
        status.analyst_operational_status
        == "DEGRADED"
    )

def test_mutating_dictionary_payload_does_not_change_later_payload(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    first_payload = status.to_dict()

    first_payload["trend_confidence"] = 10.0
    first_payload["acceptance_confidence"] = 20.0
    first_payload[
        "analyst_operational_percentage"
    ] = 100.0
    first_payload[
        "analyst_operational_status"
    ] = "OPERATIONAL"

    second_payload = status.to_dict()

    assert second_payload["trend_confidence"] == 75.0
    assert (
        second_payload["acceptance_confidence"]
        == 80.0
    )
    assert (
        second_payload[
            "analyst_operational_percentage"
        ]
        == 75.0
    )
    assert (
        second_payload["analyst_operational_status"]
        == "DEGRADED"
    )

def test_mutating_dictionary_payload_does_not_change_json_payload(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    dictionary_payload = status.to_dict()

    dictionary_payload["trend_confidence"] = 10.0
    dictionary_payload[
        "analyst_operational_percentage"
    ] = 100.0
    dictionary_payload[
        "analyst_operational_status"
    ] = "OPERATIONAL"

    json_payload = json.loads(
        status.to_json()
    )

    assert json_payload["trend_confidence"] == 75.0
    assert (
        json_payload[
            "analyst_operational_percentage"
        ]
        == 75.0
    )
    assert (
        json_payload["analyst_operational_status"]
        == "DEGRADED"
    )

def test_to_dict_returns_distinct_payload_objects(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    first_payload = status.to_dict()
    second_payload = status.to_dict()

    assert first_payload == second_payload
    assert first_payload is not second_payload

def test_mutating_one_dictionary_payload_does_not_change_another(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    first_payload = status.to_dict()
    second_payload = status.to_dict()

    first_payload["trend_confidence"] = 10.0
    first_payload["acceptance_confidence"] = 20.0

    assert second_payload["trend_confidence"] == 75.0
    assert (
        second_payload["acceptance_confidence"]
        == 80.0
    )

def test_mutating_health_related_dictionary_fields_does_not_change_later_payload(
) -> None:
    status = make_status()

    first_payload = status.to_dict()
    second_payload = status.to_dict()

    mutable_field_names = (
        field_name
        for field_name, value in first_payload.items()
        if isinstance(
            value,
            (
                dict,
                list,
            ),
        )
    )

    for field_name in mutable_field_names:
        first_value = first_payload[field_name]
        second_value = second_payload[field_name]

        assert first_value == second_value
        assert first_value is not second_value

def test_to_json_is_deterministic_for_repeated_calls(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    first_json = status.to_json()
    second_json = status.to_json()
    third_json = status.to_json()

    assert first_json == second_json
    assert second_json == third_json

def test_equivalent_status_instances_produce_identical_json(
) -> None:
    first_status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )
    second_status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    assert (
        first_status.to_json()
        == second_status.to_json()
    )

def test_integer_and_float_inputs_produce_identical_json(
) -> None:
    integer_status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )
    float_status = make_status(
        trend_confidence=75.0,
        acceptance_confidence=80.0,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75.0,
        analyst_operational_status="DEGRADED",
    )

    assert (
        integer_status.to_json()
        == float_status.to_json()
    )

def test_to_json_returns_valid_json_object(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    serialized = status.to_json()
    payload = json.loads(
        serialized
    )

    assert isinstance(
        serialized,
        str,
    )
    assert isinstance(
        payload,
        dict,
    )
    assert payload == status.to_dict()

def test_to_json_does_not_modify_later_dictionary_serialization(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    before = status.to_dict()

    status.to_json()
    status.to_json()

    after = status.to_dict()

    assert after == before

def test_different_operational_states_produce_different_json(
) -> None:
    degraded_status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )
    operational_status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=4,
        analyst_enabled_unresolved_count=0,
        analyst_operational_percentage=100,
        analyst_operational_status="OPERATIONAL",
    )

    assert (
        degraded_status.to_json()
        != operational_status.to_json()
    )

@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
def test_normalized_confidence_fields_canonicalize_negative_zero(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: -0.0,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == 0.0
    assert str(stored_value) == "0.0"

@pytest.mark.parametrize(
    "field_name",
    (
        "trend_confidence",
        "acceptance_confidence",
        "analyst_average_confidence",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_to_dict_serializes_negative_zero_as_positive_zero(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: -0.0,
        },
    )

    payload = status.to_dict()

    assert payload[field_name] == 0.0
    assert str(payload[field_name]) == "0.0"

@pytest.mark.parametrize(
    "field_name",
    (
        "trend_confidence",
        "acceptance_confidence",
        "analyst_average_confidence",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_to_json_serializes_negative_zero_as_positive_zero(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: -0.0,
        },
    )

    serialized = status.to_json()
    payload = json.loads(
        serialized
    )

    assert payload[field_name] == 0.0
    assert str(payload[field_name]) == "0.0"
    assert f'"{field_name}": -0.0' not in serialized

@pytest.mark.parametrize(
    "field_name",
    (
        "trend_confidence",
        "acceptance_confidence",
        "analyst_average_confidence",
        "analyst_coverage_percentage",
        "analyst_operational_percentage",
    ),
)
def test_normalized_confidence_fields_preserve_positive_zero(
    field_name: str,
) -> None:
    status = make_status(
        **{
            field_name: 0.0,
        },
    )

    stored_value = getattr(
        status,
        field_name,
    )

    assert stored_value == 0.0
    assert str(stored_value) == "0.0"

def test_to_json_uses_strict_json_for_valid_payload(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    serialized = status.to_json()
    payload = json.loads(
        serialized
    )

    assert payload == status.to_dict()
    assert "NaN" not in serialized
    assert "Infinity" not in serialized

@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_to_json_rejects_non_finite_value_that_bypasses_validation(
    non_finite_value: float,
) -> None:
    status = make_status(
        trend_confidence=75,
    )

    object.__setattr__(
        status,
        "trend_confidence",
        non_finite_value,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Out of range float values are not "
            "JSON compliant"
        ),
    ):
        status.to_json()

@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_to_json_rejects_non_finite_operational_percentage_bypass(
    non_finite_value: float,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    object.__setattr__(
        status,
        "analyst_operational_percentage",
        non_finite_value,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        status.to_json()

def test_to_dict_remains_plain_payload_after_validation_bypass(
) -> None:
    status = make_status(
        trend_confidence=75,
    )

    object.__setattr__(
        status,
        "trend_confidence",
        float("nan"),
    )

    payload = status.to_dict()

    assert math.isnan(
        payload["trend_confidence"]
    )

@pytest.mark.parametrize(
    "indent",
    (
        None,
        0,
        2,
        4,
    ),
)
@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_to_json_rejects_non_finite_values_for_all_indent_modes(
    indent: int | None,
    non_finite_value: float,
) -> None:
    status = make_status(
        trend_confidence=75,
    )

    object.__setattr__(
        status,
        "trend_confidence",
        non_finite_value,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        status.to_json(
            indent=indent,
        )

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_indented_json_rejects_non_finite_operational_percentage(
    indent: int,
    non_finite_value: float,
) -> None:
    status = make_status(
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    object.__setattr__(
        status,
        "analyst_operational_percentage",
        non_finite_value,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        status.to_json(
            indent=indent,
        )

@pytest.mark.parametrize(
    "indent",
    (
        None,
        0,
        2,
        4,
    ),
)
def test_to_json_indent_modes_preserve_payload(
    indent: int | None,
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    serialized = status.to_json(
        indent=indent,
    )
    payload = json.loads(
        serialized
    )

    assert payload == status.to_dict()

def test_to_json_without_indent_uses_compact_format(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    serialized = status.to_json()

    assert "\n" not in serialized
    assert ": " not in serialized
    assert ", " not in serialized

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
def test_to_json_with_indent_uses_multiline_format(
    indent: int,
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    serialized = status.to_json(
        indent=indent,
    )

    assert "\n" in serialized
    assert json.loads(
        serialized
    ) == status.to_dict()

def test_compact_json_serializes_keys_in_sorted_order(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    serialized = status.to_json()
    payload = status.to_dict()

    serialized_pairs = json.loads(
        serialized,
        object_pairs_hook=lambda pairs: pairs,
    )
    serialized_keys = tuple(
        key
        for key, _ in serialized_pairs
    )

    assert serialized_keys == tuple(
        sorted(
            payload.keys()
        )
    )

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
def test_indented_json_serializes_keys_in_sorted_order(
    indent: int,
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    serialized = status.to_json(
        indent=indent,
    )
    payload = status.to_dict()

    serialized_pairs = json.loads(
        serialized,
        object_pairs_hook=lambda pairs: pairs,
    )
    serialized_keys = tuple(
        key
        for key, _ in serialized_pairs
    )

    assert serialized_keys == tuple(
        sorted(
            payload.keys()
        )
    )

def test_compact_json_matches_canonical_encoding(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    expected = json.dumps(
        status.to_dict(),
        separators=(
            ",",
            ":",
        ),
        sort_keys=True,
        allow_nan=False,
    )

    assert status.to_json() == expected

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
def test_indented_json_matches_canonical_encoding(
    indent: int,
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
        analyst_domain_count=4,
        analyst_enabled_count=4,
        analyst_enabled_resolved_count=3,
        analyst_enabled_unresolved_count=1,
        analyst_operational_percentage=75,
        analyst_operational_status="DEGRADED",
    )

    expected = json.dumps(
        status.to_dict(),
        indent=indent,
        sort_keys=True,
        allow_nan=False,
    )

    assert status.to_json(
        indent=indent,
    ) == expected

def test_compact_json_has_no_trailing_newline(
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    serialized = status.to_json()

    assert not serialized.endswith(
        "\n"
    )

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
def test_indented_json_has_no_trailing_newline(
    indent: int,
) -> None:
    status = make_status(
        trend_confidence=75,
        acceptance_confidence=80,
    )

    serialized = status.to_json(
        indent=indent,
    )

    assert not serialized.endswith(
        "\n"
    )
