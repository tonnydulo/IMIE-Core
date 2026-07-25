from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from imie.runtime import (
    MarketSessionClock,
    MarketSessionResult,
    MarketSessionState,
    SessionPolicy,
    SessionPolicyAction,
    SessionPolicyConfig,
)


NEW_YORK = ZoneInfo(
    "America/New_York"
)


def make_session(
    state: MarketSessionState,
) -> MarketSessionResult:
    checked_at = datetime(
        2026,
        7,
        20,
        14,
        0,
        tzinfo=timezone.utc,
    )

    return MarketSessionResult(
        state=state,
        checked_at=checked_at,
        market_time=checked_at.astimezone(
            NEW_YORK
        ),
        is_trading_day=(
            state
            is not MarketSessionState.CLOSED
        ),
        reason="Test session.",
    )


@pytest.mark.parametrize(
    (
        "state",
        "expected_action",
    ),
    [
        (
            MarketSessionState.PREMARKET,
            SessionPolicyAction.ANALYZE,
        ),
        (
            MarketSessionState.REGULAR_SESSION,
            SessionPolicyAction.ANALYZE,
        ),
        (
            MarketSessionState.AFTER_HOURS,
            SessionPolicyAction.SKIP,
        ),
        (
            MarketSessionState.CLOSED,
            SessionPolicyAction.SKIP,
        ),
    ],
)
def test_default_policy(
    state: MarketSessionState,
    expected_action: SessionPolicyAction,
) -> None:
    result = SessionPolicy().evaluate(
        make_session(
            state
        )
    )

    assert result.action is expected_action
    assert (
        result.may_analyze
        is (
            expected_action
            is SessionPolicyAction.ANALYZE
        )
    )
    assert (
        result.should_skip
        is (
            expected_action
            is SessionPolicyAction.SKIP
        )
    )


def test_after_hours_can_be_enabled() -> None:
    policy = SessionPolicy(
        SessionPolicyConfig(
            allow_after_hours=True,
        )
    )

    result = policy.evaluate(
        make_session(
            MarketSessionState.AFTER_HOURS
        )
    )

    assert (
        result.action
        is SessionPolicyAction.ANALYZE
    )


def test_premarket_can_be_disabled() -> None:
    policy = SessionPolicy(
        SessionPolicyConfig(
            allow_premarket=False,
        )
    )

    result = policy.evaluate(
        make_session(
            MarketSessionState.PREMARKET
        )
    )

    assert (
        result.action
        is SessionPolicyAction.SKIP
    )


def test_closed_session_can_be_enabled() -> None:
    policy = SessionPolicy(
        SessionPolicyConfig(
            allow_closed=True,
        )
    )

    result = policy.evaluate(
        make_session(
            MarketSessionState.CLOSED
        )
    )

    assert (
        result.action
        is SessionPolicyAction.ANALYZE
    )


def test_policy_works_with_market_session_clock() -> None:
    checked_at = datetime(
        2026,
        7,
        20,
        14,
        0,
        tzinfo=timezone.utc,
    )

    session = MarketSessionClock().evaluate(
        checked_at
    )

    result = SessionPolicy().evaluate(
        session
    )

    assert (
        session.state
        is MarketSessionState.REGULAR_SESSION
    )
    assert (
        result.action
        is SessionPolicyAction.ANALYZE
    )


def test_policy_requires_session_result() -> None:
    with pytest.raises(
        TypeError,
        match="MarketSessionResult",
    ):
        SessionPolicy().evaluate(
            object(),  # type: ignore[arg-type]
        )


def test_config_must_be_session_policy_config() -> None:
    with pytest.raises(
        TypeError,
        match="SessionPolicyConfig",
    ):
        SessionPolicy(
            object(),  # type: ignore[arg-type]
        )


def test_result_reason_identifies_session() -> None:
    result = SessionPolicy().evaluate(
        make_session(
            MarketSessionState.AFTER_HOURS
        )
    )

    assert (
        "AFTER_HOURS"
        in result.reason
    )