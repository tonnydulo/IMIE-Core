from datetime import datetime, timezone

import pytest

from imie.runtime import (
    MarketSessionClock,
    SessionPolicy,
    SessionPolicyConfig,
    SessionWakePlanner,
    build_nyse_calendar,
)


def make_planner(
    *,
    allow_premarket: bool = True,
    allow_regular_session: bool = True,
    allow_after_hours: bool = False,
) -> SessionWakePlanner:
    return SessionWakePlanner(
        market_session_clock=MarketSessionClock(
            exchange_calendar=(
                build_nyse_calendar()
            )
        ),
        session_policy=SessionPolicy(
            SessionPolicyConfig(
                allow_premarket=allow_premarket,
                allow_regular_session=(
                    allow_regular_session
                ),
                allow_after_hours=allow_after_hours,
                allow_closed=False,
            )
        ),
    )


def test_before_premarket_wakes_at_four() -> None:
    result = make_planner().evaluate(
        datetime(
            2026,
            7,
            20,
            7,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.resolved is True
    assert result.next_allowed_at == datetime(
        2026,
        7,
        20,
        8,
        0,
        tzinfo=timezone.utc,
    )
    assert result.delay_seconds == 3600.0


def test_premarket_disabled_wakes_at_regular_open() -> None:
    result = make_planner(
        allow_premarket=False,
    ).evaluate(
        datetime(
            2026,
            7,
            20,
            7,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.next_allowed_at == datetime(
        2026,
        7,
        20,
        13,
        30,
        tzinfo=timezone.utc,
    )


def test_friday_night_wakes_monday_premarket() -> None:
    result = make_planner().evaluate(
        datetime(
            2026,
            7,
            18,
            0,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.next_allowed_at == datetime(
        2026,
        7,
        20,
        8,
        0,
        tzinfo=timezone.utc,
    )


def test_holiday_is_skipped() -> None:
    result = make_planner().evaluate(
        datetime(
            2026,
            7,
            3,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.next_allowed_at == datetime(
        2026,
        7,
        6,
        8,
        0,
        tzinfo=timezone.utc,
    )


def test_after_hours_can_be_next_allowed_session() -> None:
    result = make_planner(
        allow_premarket=False,
        allow_regular_session=False,
        allow_after_hours=True,
    ).evaluate(
        datetime(
            2026,
            7,
            20,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.next_allowed_at == datetime(
        2026,
        7,
        20,
        20,
        0,
        tzinfo=timezone.utc,
    )


def test_checked_at_must_be_timezone_aware() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        make_planner().evaluate(
            datetime(
                2026,
                7,
                20,
                3,
                0,
            )
        )


def test_maximum_search_days_must_be_positive() -> None:
    with pytest.raises(
        ValueError,
        match="maximum_search_days",
    ):
        SessionWakePlanner(
            market_session_clock=(
                MarketSessionClock()
            ),
            session_policy=SessionPolicy(),
            maximum_search_days=0,
        )