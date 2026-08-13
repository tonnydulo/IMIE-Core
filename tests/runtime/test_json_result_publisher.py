import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from imie.models import (
    DataFreshness,
    DecisionResult,
    DirectorDecision,
    ExecutionCandidate,
    ExecutionOrderIntent,
    PositionSizeResult,
    BrokerSubmissionResult,
    ExecutionSafetyAssessment,
    ExecutionSubmissionReservation,
)
from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    CompletedBarResult,
    JsonResultPublisher,
)


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)

BAR_TIME = datetime(
    2026,
    7,
    18,
    14,
    30,
    tzinfo=timezone.utc,
)


def make_completed_bar() -> CompletedBarResult:
    return CompletedBarResult(
        accepted=True,
        is_new=True,
        is_complete=True,
        timestamp=BAR_TIME,
        reason=(
            "A new completed market bar is available."
        ),
    )


def make_freshness() -> DataFreshness:
    return DataFreshness(
        checked_at=CHECKED_AT,
        quote_timestamp=CHECKED_AT,
        latest_bar_timestamp=BAR_TIME,
        quote_age_seconds=0.0,
        bar_age_seconds=123.0,
        quote_bar_gap_seconds=123.0,
        quote_is_fresh=True,
        bar_is_fresh=True,
        timestamps_aligned=True,
        actionable=True,
        status="FRESH",
        reason=(
            "Quote and bar data are sufficiently "
            "synchronized."
        ),
    )


def make_decision() -> DecisionResult:
    return DecisionResult(
        decision=DirectorDecision.PREPARE,
        actionable=False,
        confidence=82.5,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        reasons=(
            "Setup is developing.",
        ),
        warnings=(
            "Institutional conflict is present.",
        ),
        analyst_summary={
            "TREND": {
                "opinion": "BULLISH",
                "confidence": 90.0,
                "enabled": True,
            },
        },
    )

def make_sized_completed_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Analysis completed.",
        completed_bar=make_completed_bar(),
        freshness=make_freshness(),
        decision=make_decision(),
        position_size=make_position_size(),
        execution_candidate=(
            make_execution_candidate()
        ),
        execution_order_intent=(
            make_execution_order_intent()
        ),
        broker_submission_result=(
            make_broker_submission_result()
        ),
    )

def make_position_size() -> PositionSizeResult:
    return PositionSizeResult(
        symbol="NVDA",
        direction="long",
        account_equity=25_000.0,
        risk_percent=0.50,
        risk_budget=125.0,
        entry=100.60,
        stop=99.80,
        risk_per_share=0.80,
        quantity=156,
        position_notional=15_693.60,
        actual_risk=124.80,
        actual_risk_percent=0.4992,
        valid=True,
        actionable=True,
        reasons=(
            "Position size calculated from account risk budget.",
        ),
        warnings=(),
    )

def make_execution_candidate() -> ExecutionCandidate:
    return ExecutionCandidate(
        symbol="NVDA",
        strategy="Pullback-to-Core",
        direction="long",
        quantity=156,
        entry=100.60,
        stop=99.80,
        target1=101.40,
        target2=102.20,
        position_notional=15_693.60,
        risk_amount=124.80,
        valid=True,
        actionable=True,
        reasons=(
            "Trade plan and position size are approved.",
        ),
        warnings=(),
    )

def make_execution_order_intent() -> ExecutionOrderIntent:
    return ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=156,
        order_type="limit",
        entry_price=100.60,
        stop_price=99.80,
        target1_price=101.40,
        target2_price=102.20,
        time_in_force="day",
        valid=True,
        actionable=True,
        reasons=(
            "Execution candidate converted to order intent.",
        ),
        warnings=(),
    )

def make_broker_submission_result() -> BrokerSubmissionResult:
    return BrokerSubmissionResult(
        broker="mock",
        symbol="NVDA",
        side="buy",
        quantity=156,
        accepted=True,
        broker_order_id="mock-nvda-000001",
        status="accepted",
        message="Mock order accepted.",
        warnings=(),
    )


def make_completed_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Analysis completed.",
        completed_bar=make_completed_bar(),
        freshness=make_freshness(),
        decision=make_decision(),
    )


def make_failed_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.FAILED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Provider unavailable.",
        error_type="RuntimeError",
    )


def test_publisher_can_be_created() -> None:
    emitted: list[str] = []

    publisher = JsonResultPublisher(
        output=emitted.append,
    )

    publisher.output(
        "{}"
    )

    assert emitted == [
        "{}",
    ]


def test_output_must_be_callable() -> None:
    with pytest.raises(
        TypeError,
        match="output",
    ):
        JsonResultPublisher(
            output=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "indent",
    [
        True,
        1.5,
        "2",
    ],
)
def test_indent_must_be_int_or_none(
    indent: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="indent",
    ):
        JsonResultPublisher(
            indent=indent,  # type: ignore[arg-type]
        )


def test_indent_cannot_be_negative() -> None:
    with pytest.raises(
        ValueError,
        match="indent",
    ):
        JsonResultPublisher(
            indent=-1,
        )


def test_sort_keys_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match="sort_keys",
    ):
        JsonResultPublisher(
            sort_keys="yes",  # type: ignore[arg-type]
        )


def test_completed_result_converts_to_dict() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    payload = publisher.to_dict(
        make_completed_result()
    )

    assert payload["status"] == "COMPLETED"
    assert payload["symbol"] == "NVDA"
    assert payload["timeframe"] == "2m"
    assert payload["message"] == "Analysis completed."
    assert payload["position_size"] is None

    assert payload["completed_bar"] == {
        "accepted": True,
        "is_new": True,
        "is_complete": True,
        "timestamp": BAR_TIME.isoformat(),
        "reason": (
            "A new completed market bar is available."
        ),
    }

    assert payload["freshness"] is not None
    assert payload["freshness"]["status"] == "FRESH"
    assert (
        payload["freshness"]["actionable"]
        is True
    )

    assert payload["decision"] is not None
    assert (
        payload["decision"]["decision"]
        == "PREPARE"
    )
    assert (
        payload["decision"]["confidence"]
        == 82.5
    )
    assert payload["decision"]["reasons"] == [
        "Setup is developing.",
    ]
    assert payload["decision"]["warnings"] == [
        "Institutional conflict is present.",
    ]
    assert payload["decision"]["analyst_summary"] == {
        "TREND": {
            "opinion": "BULLISH",
            "confidence": 90.0,
            "enabled": True,
        },
    }
    assert (
        payload["decision"]["has_trade_plan"]
        is False
    )
    assert payload["execution_candidate"] is None
    assert payload["execution_order_intent"] is None


def test_failed_result_converts_to_dict() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    payload = publisher.to_dict(
        make_failed_result()
    )

    assert payload["status"] == "FAILED"
    assert payload["error_type"] == "RuntimeError"
    assert payload["completed_bar"] is None
    assert payload["freshness"] is None
    assert payload["decision"] is None
    assert payload["position_size"] is None
    assert payload["execution_candidate"] is None
    assert payload["execution_order_intent"] is None
    assert payload["broker_submission_result"] is None


def test_dumps_returns_valid_json() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
        indent=2,
    )

    serialized = publisher.dumps(
        make_completed_result()
    )

    payload = json.loads(
        serialized
    )

    assert payload["status"] == "COMPLETED"
    assert payload["decision"]["decision"] == (
        "PREPARE"
    )


def test_publish_emits_one_json_document() -> None:
    emitted: list[str] = []

    publisher = JsonResultPublisher(
        output=emitted.append,
    )

    publisher.publish(
        make_failed_result()
    )

    assert len(
        emitted
    ) == 1

    payload = json.loads(
        emitted[0]
    )

    assert payload["status"] == "FAILED"
    assert payload["error_type"] == "RuntimeError"


def test_publisher_is_callable() -> None:
    emitted: list[str] = []

    publisher = JsonResultPublisher(
        output=emitted.append,
    )

    publisher(
        make_failed_result()
    )

    assert len(
        emitted
    ) == 1


def test_result_must_be_analysis_cycle_result() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    with pytest.raises(
        TypeError,
        match="AnalysisCycleResult",
    ):
        publisher.to_dict(
            object(),  # type: ignore[arg-type]
        )

def test_position_size_converts_to_dict() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    payload = publisher.to_dict(
        make_sized_completed_result()
    )

    assert payload["position_size"] == {
        "symbol": "NVDA",
        "direction": "long",
        "account_equity": 25_000.0,
        "risk_percent": 0.50,
        "risk_budget": 125.0,
        "entry": 100.60,
        "stop": 99.80,
        "risk_per_share": 0.80,
        "quantity": 156,
        "position_notional": 15_693.60,
        "actual_risk": 124.80,
        "actual_risk_percent": 0.4992,
        "valid": True,
        "actionable": True,
        "reasons": [
            "Position size calculated from account risk budget.",
        ],
        "warnings": [],
    }

    assert payload["execution_candidate"] is not None

    execution_candidate = payload[
        "execution_candidate"
    ]

    assert execution_candidate["symbol"] == "NVDA"
    assert (
        execution_candidate["strategy"]
        == "Pullback-to-Core"
    )
    assert execution_candidate["direction"] == "long"
    assert execution_candidate["quantity"] == 156
    assert execution_candidate["entry"] == pytest.approx(
        100.60
    )
    assert execution_candidate["stop"] == pytest.approx(
        99.80
    )
    assert execution_candidate["target1"] == pytest.approx(
        101.40
    )
    assert execution_candidate["target2"] == pytest.approx(
        102.20
    )
    assert execution_candidate[
        "position_notional"
    ] == pytest.approx(
        15_693.60
    )
    assert execution_candidate[
        "risk_amount"
    ] == pytest.approx(
        124.80
    )
    assert execution_candidate["valid"] is True
    assert execution_candidate["actionable"] is True
    assert execution_candidate["reasons"] == [
        "Trade plan and position size are approved.",
    ]
    assert execution_candidate["warnings"] == []

def test_execution_order_intent_converts_to_dict() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    payload = publisher.to_dict(
        make_sized_completed_result()
    )

    assert payload["execution_order_intent"] == {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 156,
        "order_type": "limit",
        "entry_price": 100.60,
        "stop_price": 99.80,
        "target1_price": 101.40,
        "target2_price": 102.20,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
        "reasons": [
            "Execution candidate converted to order intent.",
        ],
        "warnings": [],
    }

def test_broker_submission_result_converts_to_dict() -> None:
    publisher = JsonResultPublisher(
        output=lambda value: None,
    )

    payload = publisher.to_dict(
        make_sized_completed_result()
    )

    assert payload["broker_submission_result"] == {
        "broker": "mock",
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 156,
        "accepted": True,
        "broker_order_id": "mock-nvda-000001",
        "status": "accepted",
        "message": "Mock order accepted.",
        "warnings": [],
    }


def test_execution_safety_and_reservation_convert_to_dict() -> None:
    assessment = ExecutionSafetyAssessment(
        symbol="NVDA", order_notional=15_693.60, risk_amount=124.80,
        maximum_order_notional=25_000, maximum_risk_amount=125,
        candidate_valid=True, candidate_actionable=True,
        notional_within_limit=True, risk_within_limit=True,
        allowed=True,
    )
    reservation = ExecutionSubmissionReservation(
        fingerprint="a" * 64, symbol="NVDA", side="buy", quantity=156,
        reserved_at=CHECKED_AT,
    )
    payload = JsonResultPublisher(output=lambda value: None).to_dict(
        replace(
            make_sized_completed_result(),
            execution_safety_assessment=assessment,
            execution_submission_reservation=reservation,
        )
    )

    assert payload["execution_safety_assessment"]["allowed"] is True
    assert payload["execution_safety_assessment"]["maximum_risk_amount"] == 125.0
    assert payload["execution_submission_reservation"] == {
        "fingerprint": "a" * 64,
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 156,
        "reserved_at": CHECKED_AT.isoformat(),
    }
