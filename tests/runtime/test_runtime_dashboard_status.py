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
        