import json
from datetime import datetime, timezone

import pytest

from imie.models import (
    DataFreshness,
    DecisionResult,
    DirectorDecision,
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