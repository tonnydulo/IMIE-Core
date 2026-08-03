from datetime import datetime, timedelta, timezone

import pytest

from imie.models import MarketBar
from imie.runtime import CompletedBarGuard


def make_bar(
    *,
    timestamp: datetime,
    symbol: str = "NVDA",
    timeframe: str = "2m",
) -> MarketBar:
    return MarketBar(
        symbol=symbol,
        timestamp=timestamp,
        open=100.0,
        high=101.0,
        low=99.5,
        close=100.5,
        volume=100_000,
        timeframe=timeframe,
        provider="TEST",
    )


def test_no_bars_are_rejected() -> None:
    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=3.0,
    )

    result = guard.evaluate(
        bars=[],
        checked_at=datetime(
            2026,
            7,
            18,
            14,
            32,
            3,
            tzinfo=timezone.utc,
        ),
    )

    assert result.accepted is False
    assert result.is_new is False
    assert result.is_complete is False
    assert result.timestamp is None
    assert result.reason == "No market bars are available."


def test_incomplete_bar_is_rejected() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=3.0,
    )

    result = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=timestamp
        + timedelta(
            minutes=2,
            seconds=2,
        ),
    )

    assert result.accepted is False
    assert result.is_new is True
    assert result.is_complete is False
    assert result.timestamp == timestamp
    assert result.reason == "Latest market bar has not completed."
    assert guard.last_accepted_timestamp is None


def test_completed_bar_is_accepted() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=3.0,
    )

    result = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=timestamp
        + timedelta(
            minutes=2,
            seconds=3,
        ),
    )

    assert result.accepted is True
    assert result.is_new is True
    assert result.is_complete is True
    assert result.timestamp == timestamp
    assert (
        result.reason
        == "A new completed market bar is available."
    )
    assert guard.last_accepted_timestamp == timestamp


def test_same_completed_bar_is_rejected_twice() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=0.0,
    )

    checked_at = timestamp + timedelta(
        minutes=2,
    )

    first = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=checked_at,
    )

    second = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=checked_at
        + timedelta(
            seconds=5,
        ),
    )

    assert first.accepted is True

    assert second.accepted is False
    assert second.is_new is False
    assert second.is_complete is True
    assert (
        second.reason
        == "Latest completed market bar was already processed."
    )


def test_later_completed_bar_is_accepted() -> None:
    first_timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    second_timestamp = first_timestamp + timedelta(
        minutes=2,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=0.0,
    )

    first = guard.evaluate(
        bars=[
            make_bar(
                timestamp=first_timestamp,
            ),
        ],
        checked_at=first_timestamp
        + timedelta(
            minutes=2,
        ),
    )

    second = guard.evaluate(
        bars=[
            make_bar(
                timestamp=first_timestamp,
            ),
            make_bar(
                timestamp=second_timestamp,
            ),
        ],
        checked_at=second_timestamp
        + timedelta(
            minutes=2,
        ),
    )

    assert first.accepted is True
    assert second.accepted is True
    assert second.is_new is True
    assert second.is_complete is True
    assert second.timestamp == second_timestamp
    assert guard.last_accepted_timestamp == second_timestamp


def test_older_bar_is_rejected_after_newer_bar() -> None:
    older_timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    newer_timestamp = older_timestamp + timedelta(
        minutes=2,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=0.0,
    )

    guard.evaluate(
        bars=[
            make_bar(
                timestamp=newer_timestamp,
            ),
        ],
        checked_at=newer_timestamp
        + timedelta(
            minutes=2,
        ),
    )

    result = guard.evaluate(
        bars=[
            make_bar(
                timestamp=older_timestamp,
            ),
        ],
        checked_at=newer_timestamp
        + timedelta(
            minutes=3,
        ),
    )

    assert result.accepted is False
    assert result.is_new is False
    assert result.is_complete is True
    assert (
        result.reason
        == "Latest completed market bar was already processed."
    )


def test_reset_allows_same_bar_to_be_processed_again() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
        completion_delay_seconds=0.0,
    )

    checked_at = timestamp + timedelta(
        minutes=2,
    )

    first = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=checked_at,
    )

    guard.reset()

    second = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=checked_at,
    )

    assert first.accepted is True
    assert second.accepted is True
    assert guard.last_accepted_timestamp == timestamp


def test_timezone_naive_bar_timestamp_is_rejected() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
    )

    result = guard.evaluate(
        bars=[
            make_bar(
                timestamp=timestamp,
            ),
        ],
        checked_at=datetime(
            2026,
            7,
            18,
            14,
            33,
            tzinfo=timezone.utc,
        ),
    )

    assert result.accepted is False
    assert result.is_complete is False
    assert result.timestamp == timestamp
    assert (
        result.reason
        == "Latest market bar timestamp must be timezone-aware."
    )


def test_checked_at_must_be_timezone_aware() -> None:
    timestamp = datetime(
        2026,
        7,
        18,
        14,
        30,
        tzinfo=timezone.utc,
    )

    guard = CompletedBarGuard(
        timeframe_minutes=2,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        guard.evaluate(
            bars=[
                make_bar(
                    timestamp=timestamp,
                ),
            ],
            checked_at=datetime(
                2026,
                7,
                18,
                14,
                33,
            ),
        )


def test_bars_must_be_a_list() -> None:
    guard = CompletedBarGuard(
        timeframe_minutes=2,
    )

    with pytest.raises(
        TypeError,
        match="bars must be a list",
    ):
        guard.evaluate(
            bars=(),  # type: ignore[arg-type]
            checked_at=datetime.now(
                timezone.utc
            ),
        )


def test_bars_must_contain_market_bars() -> None:
    guard = CompletedBarGuard(
        timeframe_minutes=2,
    )

    with pytest.raises(
        TypeError,
        match="MarketBar",
    ):
        guard.evaluate(
            bars=[
                object(),
            ],  # type: ignore[list-item]
            checked_at=datetime.now(
                timezone.utc
            ),
        )


def test_timeframe_minutes_must_be_positive() -> None:
    with pytest.raises(
        ValueError,
        match="timeframe_minutes",
    ):
        CompletedBarGuard(
            timeframe_minutes=0,
        )


def test_completion_delay_cannot_be_negative() -> None:
    with pytest.raises(
        ValueError,
        match="completion_delay_seconds",
    ):
        CompletedBarGuard(
            timeframe_minutes=2,
            completion_delay_seconds=-1.0,
        )