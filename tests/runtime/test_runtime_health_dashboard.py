import json

from pathlib import Path

import pytest

from imie.runtime import (
    build_dashboard_html,
    create_dashboard_server,
    read_health_status,
)


def test_read_health_status(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "health.json"
    )

    expected = {
        "state": "RUNNING",
        "completed_cycle_count": 3,
    }

    path.write_text(
        json.dumps(
            expected
        ),
        encoding="utf-8",
    )

    assert (
        read_health_status(
            path
        )
        == expected
    )


def test_read_health_status_requires_existing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        read_health_status(
            tmp_path
            / "missing.json"
        )


def test_read_health_status_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "health.json"
    )

    path.write_text(
        "{invalid",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        read_health_status(
            path
        )


def test_read_health_status_requires_object(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "health.json"
    )

    path.write_text(
        "[]",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="object",
    ):
        read_health_status(
            path
        )


def test_dashboard_html_contains_health_endpoint() -> None:
    html = build_dashboard_html(
        refresh_seconds=2.0
    )

    assert (
        "IMIE Runtime Dashboard"
        in html
    )

    assert (
        'fetch(\n                    "/api/health"'
        in html
    )

    assert (
        "2000"
        in html
    )


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        "2",
        None,
    ],
)
def test_refresh_seconds_requires_number(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="refresh_seconds",
    ):
        build_dashboard_html(
            refresh_seconds=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
    ],
)
def test_refresh_seconds_must_be_positive(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        build_dashboard_html(
            refresh_seconds=value
        )


def test_create_dashboard_server(
    tmp_path: Path,
) -> None:
    server = create_dashboard_server(
        health_status_file=(
            tmp_path
            / "health.json"
        ),
        host="127.0.0.1",
        port=8765,
    )

    try:
        assert (
            server.server_address[0]
            == "127.0.0.1"
        )

        assert (
            server.server_address[1]
            == 8765
        )
    finally:
        server.server_close()


@pytest.mark.parametrize(
    "port",
    [
        0,
        -1,
        65536,
    ],
)
def test_dashboard_port_validation(
    tmp_path: Path,
    port: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="port",
    ):
        create_dashboard_server(
            health_status_file=(
                tmp_path
                / "health.json"
            ),
            port=port,
        )

def test_dashboard_html_contains_extended_fields() -> None:
    html = build_dashboard_html(
        refresh_seconds=2.0
    )

    assert 'id="symbol"' in html
    assert 'id="timeframe"' in html
    assert 'id="marketSession"' in html
    assert 'id="latestDecision"' in html
    assert 'id="latestCycleStatus"' in html
    assert 'id="latestCycleStarted"' in html
    assert 'id="latestCycleCompleted"' in html
    assert 'id="latestCycleMessage"' in html

def test_dashboard_html_reads_extended_payload_fields() -> None:
    html = build_dashboard_html(
        refresh_seconds=2.0
    )

    assert "payload.symbol" in html
    assert "payload.timeframe" in html
    assert "payload.market_session" in html
    assert "payload.latest_decision" in html
    assert "payload.latest_cycle_status" in html
    assert "payload.latest_cycle_message" in html
    assert "payload.latest_cycle_started_at" in html
    assert "payload.latest_cycle_completed_at" in html
    assert "payload.latest_error_type" in html

def test_dashboard_html_contains_cycle_styling() -> None:
    html = build_dashboard_html(
        refresh_seconds=2.0
    )

    assert "cycle-completed" in html
    assert "cycle-skipped" in html
    assert "cycle-failed" in html
    assert "decision-ready" in html
    assert "decision-wait" in html

def test_dashboard_html_contains_decision_detail_fields() -> None:
    html = build_dashboard_html()

    assert 'id="decisionConfidence"' in html
    assert 'id="decisionActionable"' in html
    assert 'id="tradeDirection"' in html
    assert 'id="decisionRecommendation"' in html

    assert (
        "payload.decision_confidence"
        in html
    )

    assert (
        "payload.decision_actionable"
        in html
    )

    assert (
        "payload.trade_direction"
        in html
    )

    assert (
        "payload.decision_recommendation"
        in html
    )


def test_dashboard_html_contains_decision_formatters() -> None:
    html = build_dashboard_html()

    assert "function formatConfidence" in html
    assert "function updateActionable" in html
    assert "function updateTradeDirection" in html

    assert '"actionable-yes"' in html
    assert '"actionable-no"' in html
    assert '"direction-long"' in html
    assert '"direction-short"' in html

def test_dashboard_html_contains_trade_plan_fields() -> None:
    html = build_dashboard_html()

    assert 'id="tradePlanValid"' in html
    assert 'id="tradeEntry"' in html
    assert 'id="tradeStop"' in html
    assert 'id="tradeTarget1"' in html
    assert 'id="tradeTarget2"' in html
    assert 'id="tradeRR1"' in html
    assert 'id="tradeRR2"' in html
    assert 'id="tradeQuality"' in html

    assert "payload.trade_plan_valid" in html
    assert "payload.trade_entry" in html
    assert "payload.trade_stop" in html
    assert "payload.trade_target1" in html
    assert "payload.trade_target2" in html
    assert "payload.trade_rr1" in html
    assert "payload.trade_rr2" in html
    assert "payload.trade_quality" in html

def test_dashboard_html_contains_trade_plan_formatters() -> None:
    html = build_dashboard_html()

    assert "function formatTradePrice" in html
    assert "function formatRewardRisk" in html
    assert "function updateTradePlanValid" in html
    assert "function updateTradeQuality" in html

    assert '"plan-valid"' in html
    assert '"plan-invalid"' in html
    assert '"trade-quality-high"' in html
    assert '"trade-quality-medium"' in html
    assert '"trade-quality-low"' in html

def test_dashboard_html_contains_trade_explanation_fields() -> None:
    html = build_dashboard_html()

    assert 'id="tradeNarrative"' in html
    assert 'id="tradeReasons"' in html
    assert 'id="tradeWarnings"' in html

    assert "payload.trade_narrative" in html
    assert "payload.trade_reasons" in html
    assert "payload.trade_warnings" in html

def test_dashboard_html_contains_trade_explanation_renderer() -> None:
    html = build_dashboard_html()

    assert "function updateTextList" in html
    assert "document.createElement" in html
    assert "element.replaceChildren" in html

    assert "No trade reasons available." in html
    assert "No trade warnings." in html
    assert '"empty-list"' in html

def test_dashboard_html_contains_institutional_context_fields() -> None:
    html = build_dashboard_html()

    assert 'id="institutionalBias"' in html
    assert 'id="institutionalBiasConfidence"' in html
    assert 'id="marketPhase"' in html
    assert 'id="marketPhaseConfidence"' in html
    assert 'id="confluenceDirection"' in html
    assert 'id="confluenceScore"' in html
    assert 'id="confluenceAgreementCount"' in html
    assert 'id="confluenceConflictCount"' in html

    assert "payload.institutional_bias" in html
    assert (
        "payload.institutional_bias_confidence"
        in html
    )
    assert "payload.market_phase" in html
    assert (
        "payload.market_phase_confidence"
        in html
    )
    assert "payload.confluence_direction" in html
    assert "payload.confluence_score" in html
    assert (
        "payload.confluence_agreement_count"
        in html
    )
    assert (
        "payload.confluence_conflict_count"
        in html
    )

def test_dashboard_html_contains_institutional_renderers() -> None:
    html = build_dashboard_html()

    assert (
        "function updateInstitutionalDirection"
        in html
    )

    assert (
        "function updatePercentageMetric"
        in html
    )

    assert (
        "function updateInstitutionalCount"
        in html
    )

    assert '"institution-bullish"' in html
    assert '"institution-bearish"' in html
    assert '"institution-neutral"' in html
    assert '"institution-unknown"' in html

    assert '"metric-good"' in html
    assert '"metric-medium"' in html
    assert '"metric-low"' in html

    assert '"conflict-clear"' in html
    assert '"conflict-present"' in html

def test_dashboard_institutional_count_renderer_uses_valid_javascript() -> None:
    html = build_dashboard_html()

    assert (
        "function updateInstitutionalCount(\n"
        "            id,\n"
        "            value,\n"
        "            conflict = false"
        in html
    )

    assert "*,\n            conflict" not in html

def test_dashboard_html_contains_market_phase_detail_fields() -> None:
    html = build_dashboard_html()

    assert 'id="marketPhaseStrength"' in html

    assert (
        'id="marketPhaseAgreementCount"'
        in html
    )

    assert (
        'id="marketPhaseConflictCount"'
        in html
    )

    assert (
        'id="marketPhaseSupportingDomains"'
        in html
    )

    assert (
        'id="marketPhaseOpposingDomains"'
        in html
    )

    assert "payload.market_phase_strength" in html

    assert (
        "payload.market_phase_agreement_count"
        in html
    )

    assert (
        "payload.market_phase_conflict_count"
        in html
    )

    assert (
        "payload.market_phase_supporting_domains"
        in html
    )

    assert (
        "payload.market_phase_opposing_domains"
        in html
    )

def test_dashboard_html_contains_market_phase_domain_lists() -> None:
    html = build_dashboard_html()

    assert ".domain-list" in html
    assert ".supporting-domain-list" in html
    assert ".opposing-domain-list" in html

    assert (
        'class="domain-list supporting-domain-list"'
        in html
    )

    assert (
        'class="domain-list opposing-domain-list"'
        in html
    )

    assert "No supporting phase domains." in html
    assert "No opposing phase domains." in html

def test_dashboard_market_phase_detail_reuses_existing_renderers() -> None:
    html = build_dashboard_html()

    assert (
        'updatePercentageMetric(\n'
        '                    "marketPhaseStrength"'
        in html
    )

    assert (
        'updateInstitutionalCount(\n'
        '                    "marketPhaseAgreementCount"'
        in html
    )

    assert (
        'updateInstitutionalCount(\n'
        '                    "marketPhaseConflictCount"'
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "marketPhaseSupportingDomains"'
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "marketPhaseOpposingDomains"'
        in html
    )

def test_dashboard_html_contains_institutional_bias_detail_fields() -> None:
    html = build_dashboard_html()

    assert 'id="institutionalBiasStrength"' in html

    assert (
        'id="institutionalBiasBullishScore"'
        in html
    )

    assert (
        'id="institutionalBiasBearishScore"'
        in html
    )

    assert (
        'id="institutionalBiasAgreementCount"'
        in html
    )

    assert (
        'id="institutionalBiasConflictCount"'
        in html
    )

    assert (
        'id="institutionalBiasSupportingDomains"'
        in html
    )

    assert (
        'id="institutionalBiasOpposingDomains"'
        in html
    )

    assert (
        "payload.institutional_bias_strength"
        in html
    )

    assert (
        "payload.institutional_bias_bullish_score"
        in html
    )

    assert (
        "payload.institutional_bias_bearish_score"
        in html
    )

    assert (
        "payload.institutional_bias_agreement_count"
        in html
    )

    assert (
        "payload.institutional_bias_conflict_count"
        in html
    )

    assert (
        "payload.institutional_bias_supporting_domains"
        in html
    )

    assert (
        "payload.institutional_bias_opposing_domains"
        in html
    )

def test_dashboard_html_contains_institutional_bias_domain_lists() -> None:
    html = build_dashboard_html()

    assert (
        'class="domain-list supporting-domain-list"'
        in html
    )

    assert (
        'class="domain-list opposing-domain-list"'
        in html
    )

    assert "No supporting bias domains." in html
    assert "No opposing bias domains." in html

def test_dashboard_institutional_bias_detail_reuses_existing_renderers() -> None:
    html = build_dashboard_html()

    assert (
        'updatePercentageMetric(\n'
        '                    "institutionalBiasStrength"'
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "institutionalBiasBullishScore"'
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "institutionalBiasBearishScore"'
        in html
    )

    assert (
        'updateInstitutionalCount(\n'
        '                    "institutionalBiasAgreementCount"'
        in html
    )

    assert (
        'updateInstitutionalCount(\n'
        '                    "institutionalBiasConflictCount"'
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "institutionalBiasSupportingDomains"'
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "institutionalBiasOpposingDomains"'
        in html
    )

def test_dashboard_contains_confluence_detail_elements() -> None:
    html = build_dashboard_html()

    expected_ids = (
        "confluenceConfidenceAdjustment",
        "confluenceStructureSupport",
        "confluenceLiquiditySupport",
        "confluenceOrderBlockSupport",
        "confluenceAuctionSupport",
        "confluencePressureSupport",
        "confluenceParticipationSupport",
        "confluenceValueSupport",
        "confluenceBullishCount",
        "confluenceBearishCount",
        "confluenceNeutralCount",
        "confluenceUnknownCount",
        "confluenceDomainCount",
    )

    for element_id in expected_ids:
        assert f'id="{element_id}"' in html


def test_dashboard_contains_confluence_detail_renderers() -> None:
    html = build_dashboard_html()

    assert "function updateSupportFlag(" in html
    assert "function updateConfidenceAdjustment(" in html
    assert '"SUPPORT"' in html
    assert '"NO SUPPORT"' in html


def test_dashboard_formats_confluence_confidence_adjustment() -> None:
    html = build_dashboard_html()

    assert '"+"' in html
    assert "normalized.toFixed(0)" in html
    assert "normalized >= 6" in html
    assert "normalized >= 3" in html


def test_dashboard_updates_confluence_detail_fields() -> None:
    html = build_dashboard_html()

    expected_fields = (
        "payload.confluence_confidence_adjustment",
        "payload.confluence_structure_support",
        "payload.confluence_liquidity_support",
        "payload.confluence_order_block_support",
        "payload.confluence_auction_support",
        "payload.confluence_pressure_support",
        "payload.confluence_participation_support",
        "payload.confluence_value_support",
        "payload.confluence_bullish_count",
        "payload.confluence_bearish_count",
        "payload.confluence_neutral_count",
        "payload.confluence_unknown_count",
        "payload.confluence_domain_count",
    )

    for field in expected_fields:
        assert field in html


def test_confluence_renderers_support_missing_values() -> None:
    html = build_dashboard_html()

    assert "supported === true" in html
    assert "supported === false" in html
    assert "value === null" in html
    assert "value === undefined" in html
    assert 'element.textContent = "—"' in html


def test_dashboard_confluence_detail_uses_correct_renderers() -> None:
    html = build_dashboard_html()

    assert (
        "updateConfidenceAdjustment(\n"
        "                    "
        "payload.confluence_confidence_adjustment"
        in html
    )

    support_fields = (
        (
            "confluenceStructureSupport",
            "confluence_structure_support",
        ),
        (
            "confluenceLiquiditySupport",
            "confluence_liquidity_support",
        ),
        (
            "confluenceOrderBlockSupport",
            "confluence_order_block_support",
        ),
        (
            "confluenceAuctionSupport",
            "confluence_auction_support",
        ),
        (
            "confluencePressureSupport",
            "confluence_pressure_support",
        ),
        (
            "confluenceParticipationSupport",
            "confluence_participation_support",
        ),
        (
            "confluenceValueSupport",
            "confluence_value_support",
        ),
    )

    for element_id, payload_field in support_fields:
        assert (
            "updateSupportFlag(\n"
            f'                    "{element_id}",\n'
            f"                    payload.{payload_field}"
            in html
        )

    count_fields = (
        (
            "confluenceBullishCount",
            "confluence_bullish_count",
        ),
        (
            "confluenceBearishCount",
            "confluence_bearish_count",
        ),
        (
            "confluenceNeutralCount",
            "confluence_neutral_count",
        ),
        (
            "confluenceUnknownCount",
            "confluence_unknown_count",
        ),
        (
            "confluenceDomainCount",
            "confluence_domain_count",
        ),
    )

    for element_id, payload_field in count_fields:
        assert (
            "updateInstitutionalCount(\n"
            f'                    "{element_id}",\n'
            f"                    payload.{payload_field}"
            in html
        )

def test_dashboard_contains_setup_lifecycle_detail_fields() -> None:
    html = build_dashboard_html()

    expected_ids = (
        "setupLifecycleState",
        "setupLifecycleDirection",
        "setupLifecycleConfidence",
        "setupLifecycleAtrDistance",
        "setupLifecycleAction",
        "setupLifecycleReason",
    )

    for element_id in expected_ids:
        assert f'id="{element_id}"' in html

def test_dashboard_reads_setup_lifecycle_payload_fields() -> None:
    html = build_dashboard_html()

    expected_fields = (
        "payload.setup_lifecycle_state",
        "payload.setup_lifecycle_direction",
        "payload.setup_lifecycle_confidence",
        "payload.setup_lifecycle_atr_distance",
        "payload.setup_lifecycle_action",
        "payload.setup_lifecycle_reason",
    )

    for field in expected_fields:
        assert field in html

def test_dashboard_contains_setup_lifecycle_atr_formatter() -> None:
    html = build_dashboard_html()

    assert "function formatAtrDistance(" in html
    assert "Number(value).toFixed(2)" in html
    assert '" ATR"' in html


def test_dashboard_setup_lifecycle_reuses_existing_renderers() -> None:
    html = build_dashboard_html()

    assert (
        'setText(\n'
        '                    "setupLifecycleState",\n'
        "                    payload.setup_lifecycle_state"
        in html
    )

    assert (
        'setText(\n'
        '                    "setupLifecycleDirection",\n'
        "                    payload.setup_lifecycle_direction"
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "setupLifecycleConfidence",\n'
        "                    payload.setup_lifecycle_confidence"
        in html
    )

    assert (
        'formatAtrDistance(\n'
        "                        "
        "payload.setup_lifecycle_atr_distance"
        in html
    )

    assert (
        'setText(\n'
        '                    "setupLifecycleAction",\n'
        "                    payload.setup_lifecycle_action"
        in html
    )

    assert (
        'setText(\n'
        '                    "setupLifecycleReason",\n'
        "                    payload.setup_lifecycle_reason"
        in html
    )

def test_dashboard_contains_acceptance_detail_fields() -> None:
    html = build_dashboard_html()

    expected_ids = (
        "acceptanceConfirmed",
        "acceptanceDirection",
        "acceptanceLevel",
        "acceptanceScore",
        "acceptanceConfidence",
        "acceptanceTriggerPrice",
        "acceptancePreviousLevel",
        "acceptancePullbackLow",
        "acceptancePullbackHigh",
        "acceptanceReason",
        "acceptanceEvidence",
        "acceptanceWarnings",
    )

    for element_id in expected_ids:
        assert f'id="{element_id}"' in html

def test_dashboard_reads_acceptance_payload_fields() -> None:
    html = build_dashboard_html()

    expected_fields = (
        "payload.acceptance_confirmed",
        "payload.acceptance_direction",
        "payload.acceptance_level",
        "payload.acceptance_score",
        "payload.acceptance_confidence",
        "payload.acceptance_trigger_price",
        "payload.acceptance_previous_level",
        "payload.acceptance_pullback_low",
        "payload.acceptance_pullback_high",
        "payload.acceptance_reason",
        "payload.acceptance_evidence",
        "payload.acceptance_warnings",
    )

    for field in expected_fields:
        assert field in html

def test_dashboard_contains_acceptance_renderer() -> None:
    html = build_dashboard_html()

    assert "function updateAcceptanceConfirmed(" in html
    assert '"CONFIRMED"' in html
    assert '"NOT CONFIRMED"' in html
    assert '"plan-valid"' in html
    assert '"plan-invalid"' in html

def test_dashboard_acceptance_detail_reuses_existing_renderers() -> None:
    html = build_dashboard_html()

    assert (
        "updateAcceptanceConfirmed(\n"
        "                    payload.acceptance_confirmed"
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "acceptanceScore",\n'
        "                    payload.acceptance_score"
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "acceptanceConfidence",\n'
        "                    payload.acceptance_confidence"
        in html
    )

    price_fields = (
        (
            "acceptanceTriggerPrice",
            "acceptance_trigger_price",
        ),
        (
            "acceptancePreviousLevel",
            "acceptance_previous_level",
        ),
        (
            "acceptancePullbackLow",
            "acceptance_pullback_low",
        ),
        (
            "acceptancePullbackHigh",
            "acceptance_pullback_high",
        ),
    )

    for element_id, payload_field in price_fields:
        assert (
            'setText(\n'
            f'                    "{element_id}",\n'
            "                    formatTradePrice(\n"
            f"                        payload.{payload_field}"
            in html
        )

    assert (
        'updateTextList(\n'
        '                    "acceptanceEvidence",\n'
        "                    payload.acceptance_evidence"
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "acceptanceWarnings",\n'
        "                    payload.acceptance_warnings"
        in html
    )

def test_dashboard_contains_trend_detail_fields() -> None:
    html = build_dashboard_html()

    expected_ids = (
        "trendAnalyst",
        "trendOpinion",
        "trendConfidence",
        "trendEnabled",
        "trendEvidence",
        "trendWarnings",
    )

    for element_id in expected_ids:
        assert f'id="{element_id}"' in html

def test_dashboard_reads_trend_payload_fields() -> None:
    html = build_dashboard_html()

    expected_fields = (
        "payload.trend_analyst",
        "payload.trend_opinion",
        "payload.trend_confidence",
        "payload.trend_enabled",
        "payload.trend_evidence",
        "payload.trend_warnings",
    )

    for field in expected_fields:
        assert field in html

def test_dashboard_contains_trend_enabled_renderer() -> None:
    html = build_dashboard_html()

    assert "function updateTrendEnabled(" in html
    assert '"ENABLED"' in html
    assert '"DISABLED"' in html
    assert '"plan-valid"' in html
    assert '"plan-invalid"' in html

def test_dashboard_trend_detail_reuses_existing_renderers() -> None:
    html = build_dashboard_html()

    assert (
        'setText(\n'
        '                    "trendAnalyst",\n'
        "                    payload.trend_analyst"
        in html
    )

    assert (
        'setText(\n'
        '                    "trendOpinion",\n'
        "                    payload.trend_opinion"
        in html
    )

    assert (
        'updatePercentageMetric(\n'
        '                    "trendConfidence",\n'
        "                    payload.trend_confidence"
        in html
    )

    assert (
        "updateTrendEnabled(\n"
        "                    payload.trend_enabled"
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "trendEvidence",\n'
        "                    payload.trend_evidence"
        in html
    )

    assert (
        'updateTextList(\n'
        '                    "trendWarnings",\n'
        "                    payload.trend_warnings"
        in html
    )

