from datetime import datetime, timezone

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
)


def make_time(
    minute: int = 30,
) -> datetime:
    return datetime(
        2026,
        7,
        18,
        14,
        minute,
        tzinfo=timezone.utc,
    )


def test_skipped_cycle_can_be_created() -> None:
    result = AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol=" nvda ",
        timeframe="2M",
        started_at=make_time(),
        completed_at=make_time(),
        message=" No new completed bar. ",
    )

    assert result.symbol == "NVDA"
    assert result.timeframe == "2m"
    assert result.message == "No new completed bar."
    assert result.succeeded is False
    assert result.skipped is True
    assert result.failed is False


def test_failed_cycle_requires_error_type() -> None:
    with pytest.raises(
        ValueError,
        match="error_type",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.FAILED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle failed.",
        )


def test_failed_cycle_is_identified() -> None:
    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.FAILED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Provider failed.",
        error_type=" RuntimeError ",
    )

    assert result.failed is True
    assert result.error_type == "RuntimeError"


def test_completed_cycle_requires_decision() -> None:
    with pytest.raises(
        ValueError,
        match="decision",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
        )


def test_stale_cycle_requires_freshness() -> None:
    with pytest.raises(
        ValueError,
        match="freshness",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.STALE_DATA,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Market data is stale.",
        )


def test_completion_cannot_precede_start() -> None:
    with pytest.raises(
        ValueError,
        match="completed_at",
    ):
        AnalysisCycleResult(
            status=(
                AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
            ),
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(
                minute=31,
            ),
            completed_at=make_time(
                minute=30,
            ),
            message="Skipped.",
        )


def test_timestamps_must_be_timezone_aware() -> None:
    with pytest.raises(
        ValueError,
        match="started_at",
    ):
        AnalysisCycleResult(
            status=(
                AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
            ),
            symbol="NVDA",
            timeframe="2m",
            started_at=datetime(
                2026,
                7,
                18,
                14,
                30,
            ),
            completed_at=make_time(),
            message="Skipped.",
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "field_value",
    ),
    [
        (
            "symbol",
            " ",
        ),
        (
            "timeframe",
            "",
        ),
        (
            "message",
            " ",
        ),
    ],
)
def test_required_text_cannot_be_empty(
    field_name: str,
    field_value: str,
) -> None:
    arguments = {
        "status": (
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        "symbol": "NVDA",
        "timeframe": "2m",
        "started_at": make_time(),
        "completed_at": make_time(),
        "message": "Skipped.",
    }

    arguments[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AnalysisCycleResult(
            **arguments,  # type: ignore[arg-type]
        )