from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import ExecutionDataFreshnessEngine
from imie.models import DataFreshness, ExecutionDataFreshnessAssessment


NOW = datetime(2026, 8, 14, 15, 30, tzinfo=timezone.utc)


def freshness(**overrides):
    values = {
        "checked_at": NOW,
        "quote_timestamp": NOW - timedelta(seconds=1),
        "latest_bar_timestamp": NOW - timedelta(seconds=2),
        "quote_age_seconds": 1,
        "bar_age_seconds": 2,
        "quote_bar_gap_seconds": 1,
        "quote_is_fresh": True,
        "bar_is_fresh": True,
        "timestamps_aligned": True,
        "actionable": True,
        "status": "FRESH",
        "reason": "Market data is fresh and aligned.",
    }
    values.update(overrides)
    return DataFreshness(**values)


def test_verified_actionable_freshness_is_allowed():
    assessment = ExecutionDataFreshnessEngine().assess(freshness())

    assert isinstance(assessment, ExecutionDataFreshnessAssessment)
    assert assessment.allowed is True
    assert assessment.source_actionable is True
    assert assessment.quote_age_seconds == 1.0
    assert assessment.bar_age_seconds == 2.0
    assert assessment.violations == ()


@pytest.mark.parametrize(
    "overrides, violation",
    [
        (
            {"quote_is_fresh": False, "actionable": False},
            "Market quote is stale.",
        ),
        (
            {"bar_is_fresh": False, "actionable": False},
            "Latest market bar is stale.",
        ),
        (
            {"timestamps_aligned": False, "actionable": False},
            "Quote and bar timestamps are not aligned.",
        ),
    ],
)
def test_unverified_market_data_is_blocked(overrides, violation):
    assessment = ExecutionDataFreshnessEngine().assess(
        freshness(**overrides)
    )

    assert assessment.allowed is False
    assert violation in assessment.violations


def test_non_actionable_source_cannot_pass_even_when_flags_are_fresh():
    assessment = ExecutionDataFreshnessEngine().assess(
        freshness(actionable=False, reason="Manual freshness denial.")
    )

    assert assessment.allowed is False
    assert assessment.violations == (
        "Data freshness guard did not authorize execution: "
        "Manual freshness denial.",
    )


def test_all_freshness_violations_are_preserved():
    assessment = ExecutionDataFreshnessEngine().assess(
        freshness(
            quote_is_fresh=False,
            bar_is_fresh=False,
            timestamps_aligned=False,
            actionable=False,
        )
    )

    assert assessment.violations == (
        "Market quote is stale.",
        "Latest market bar is stale.",
        "Quote and bar timestamps are not aligned.",
    )


@pytest.mark.parametrize("value", [None, object(), "fresh"])
def test_engine_rejects_invalid_freshness(value):
    with pytest.raises(TypeError, match="DataFreshness"):
        ExecutionDataFreshnessEngine().assess(value)


def test_invalid_numeric_truth_fails_closed():
    with pytest.raises(ValueError, match="quote_age_seconds"):
        ExecutionDataFreshnessEngine().assess(
            freshness(quote_age_seconds=-1)
        )


def test_naive_timestamp_truth_fails_closed():
    with pytest.raises(ValueError, match="checked_at"):
        ExecutionDataFreshnessEngine().assess(
            freshness(checked_at=datetime(2026, 8, 14, 15, 30))
        )
