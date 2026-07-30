import json

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

def test_status_accepts_analyst_coverage_message() -> None:
    status = make_status(
        analyst_coverage_message=(
            "6 of 8 analyst domains have produced an opinion."
        ),
    )

    assert status.analyst_coverage_message == (
        "6 of 8 analyst domains have produced an opinion."
    )

def test_status_normalizes_analyst_coverage_message() -> None:
    status = make_status(
        analyst_coverage_message=(
            "  All analyst domains are resolved.  "
        ),
    )

    assert status.analyst_coverage_message == (
        "All analyst domains are resolved."
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

def test_status_serializes_analyst_coverage_message() -> None:
    status = make_status(
        analyst_coverage_message=(
            "All 8 analyst domains have produced an opinion."
        ),
    )

    payload = status.to_dict()

    assert payload["analyst_coverage_message"] == (
        "All 8 analyst domains have produced an opinion."
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
        analyst_operational_message=(
            "  All enabled analyst domains "
            "have produced an opinion.  "
        )
    )

    assert (
        status.analyst_operational_message
        == (
            "All enabled analyst domains "
            "have produced an opinion."
        )
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
    "kwargs",
    [
        {
            "analyst_domain_count": 0,
            "analyst_confidence_count": 0,
            "analyst_confidence_coverage_percentage": 10.0,
        },
        {
            "analyst_enabled_count": 0,
            "analyst_enabled_confidence_count": 0,
            "analyst_enabled_confidence_coverage_percentage": 10.0,
        },
    ],
)

def test_zero_confidence_denominator_rejects_nonzero_percentage(
    kwargs: dict[str, int | float],
) -> None:
    with pytest.raises(
        ValueError,
        match="must agree",
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
        "invalid_state",
    ),
    [
        (0, 0, "COMPLETE"),
        (4, 0, "PARTIAL"),
        (4, 2, "COMPLETE"),
        (4, 4, "MISSING"),
    ],
)

def test_confidence_coverage_state_rejects_inconsistent_counts(
    domain_count: int,
    confidence_count: int,
    invalid_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_confidence_coverage_state "
            "must agree"
        ),
    ):
        make_status(
            analyst_domain_count=domain_count,
            analyst_confidence_count=confidence_count,
            analyst_confidence_coverage_state=(
                invalid_state
            ),
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
    ),
    [
        (0, 0, 0, "DISABLED"),
        (4, 0, 0, "UNAVAILABLE"),
        (4, 3, 0, "PARTIAL"),
        (4, 3, 1, "COMPLETE"),
        (4, 3, 3, "MISSING"),
    ],
)

def test_enabled_confidence_coverage_state_rejects_inconsistent_counts(
    domain_count: int,
    enabled_count: int,
    enabled_confidence_count: int,
    invalid_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "analyst_enabled_confidence_coverage_state "
            "must agree"
        ),
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

