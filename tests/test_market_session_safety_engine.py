from datetime import datetime, timezone

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
