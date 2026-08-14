from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import BrokerMarketSessionPort, MarketSessionSafetyEngine
from imie.models import BrokerMarketSessionSnapshot


NOW = datetime(2026, 8, 14, 14, 30, tzinfo=timezone.utc)
NEXT_OPEN = datetime(2026, 8, 17, 13, 30, tzinfo=timezone.utc)
NEXT_CLOSE = datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc)


class SessionSource:
    def get_market_session(self):
        return BrokerMarketSessionSnapshot(
            broker="alpaca-paper",
            is_open=True,
            observed_at=NOW,
            next_close=NEXT_CLOSE,
        )


def test_market_session_port_is_runtime_checkable():
    assert isinstance(SessionSource(), BrokerMarketSessionPort)


def test_open_broker_session_is_allowed():
    assessment = MarketSessionSafetyEngine().assess(
        SessionSource().get_market_session()
    )

    assert assessment.broker == "alpaca-paper"
    assert assessment.session_open is True
    assert assessment.allowed is True
    assert assessment.next_close == NEXT_CLOSE
    assert assessment.violations == ()


def test_closed_broker_session_is_blocked():
    snapshot = BrokerMarketSessionSnapshot(
        broker="alpaca-paper",
        is_open=False,
        observed_at=NOW,
        next_open=NEXT_OPEN,
    )

    assessment = MarketSessionSafetyEngine().assess(snapshot)

    assert assessment.session_open is False
    assert assessment.allowed is False
    assert assessment.next_open == NEXT_OPEN
    assert assessment.violations == ("Broker market session is closed.",)


def test_fresh_open_session_is_allowed_at_exact_age_boundary():
    assessment = MarketSessionSafetyEngine().assess(
        SessionSource().get_market_session(),
        checked_at=NOW + timedelta(seconds=5),
        maximum_session_age_seconds=5,
    )

    assert assessment.allowed is True
    assert assessment.session_age_seconds == 5.0
    assert assessment.maximum_session_age_seconds == 5.0
    assert assessment.session_fresh is True


def test_stale_open_session_is_blocked():
    assessment = MarketSessionSafetyEngine().assess(
        SessionSource().get_market_session(),
        checked_at=NOW + timedelta(seconds=5.001),
        maximum_session_age_seconds=5,
    )

    assert assessment.session_open is True
    assert assessment.session_fresh is False
    assert assessment.allowed is False
    assert assessment.violations == (
        "Broker market session is stale: 5.001s > 5.000s.",
    )


def test_closed_and_stale_session_reports_both_violations():
    snapshot = BrokerMarketSessionSnapshot(
        broker="alpaca-paper", is_open=False, observed_at=NOW
    )

    assessment = MarketSessionSafetyEngine().assess(
        snapshot,
        checked_at=NOW + timedelta(seconds=6),
        maximum_session_age_seconds=5,
    )

    assert assessment.violations == (
        "Broker market session is stale: 6.000s > 5.000s.",
        "Broker market session is closed.",
    )


def test_future_session_observation_fails_closed():
    with pytest.raises(ValueError, match="future"):
        MarketSessionSafetyEngine().assess(
            SessionSource().get_market_session(),
            checked_at=NOW - timedelta(microseconds=1),
            maximum_session_age_seconds=5,
        )


@pytest.mark.parametrize(
    "checked_at, maximum_age",
    [(NOW, None), (None, 5)],
)
def test_freshness_configuration_must_be_complete(checked_at, maximum_age):
    with pytest.raises(ValueError, match="configured together"):
        MarketSessionSafetyEngine().assess(
            SessionSource().get_market_session(),
            checked_at=checked_at,
            maximum_session_age_seconds=maximum_age,
        )


@pytest.mark.parametrize("value", [0, -1, True, float("inf")])
def test_maximum_session_age_must_be_positive(value):
    with pytest.raises((TypeError, ValueError)):
        MarketSessionSafetyEngine().assess(
            SessionSource().get_market_session(),
            checked_at=NOW,
            maximum_session_age_seconds=value,
        )


@pytest.mark.parametrize("value", [None, "open", True])
def test_engine_rejects_invalid_snapshot(value):
    with pytest.raises(TypeError, match="BrokerMarketSessionSnapshot"):
        MarketSessionSafetyEngine().assess(value)


def test_snapshot_requires_timezone_aware_observation():
    with pytest.raises(ValueError, match="timezone-aware"):
        BrokerMarketSessionSnapshot(
            broker="alpaca-paper",
            is_open=True,
            observed_at=datetime(2026, 8, 14, 14, 30),
        )


def test_snapshot_normalizes_broker_name():
    snapshot = BrokerMarketSessionSnapshot(
        broker=" Alpaca-Paper ",
        is_open=False,
        observed_at=NOW,
    )

    assert snapshot.broker == "alpaca-paper"
