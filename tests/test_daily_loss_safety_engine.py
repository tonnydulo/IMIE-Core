from datetime import datetime, timezone

import pytest

from imie.execution import BrokerDailyPnlPort, DailyLossSafetyEngine
from imie.models import BrokerDailyPnlSnapshot, DailyLossAssessment


NOW = datetime(2026, 8, 14, 17, 0, tzinfo=timezone.utc)


def snapshot(realized=0.0, unrealized=0.0):
    return BrokerDailyPnlSnapshot(
        broker="alpaca-paper",
        realized_pnl=realized,
        unrealized_pnl=unrealized,
        observed_at=NOW,
    )


def test_profitable_day_is_allowed():
    result = DailyLossSafetyEngine().assess(
        snapshot=snapshot(realized=100, unrealized=25),
        maximum_daily_loss=250,
    )

    assert isinstance(result, DailyLossAssessment)
    assert result.total_pnl == 125.0
    assert result.loss_amount == 0.0
    assert result.allowed is True
    assert result.violations == ()


def test_combined_realized_and_unrealized_loss_is_assessed():
    result = DailyLossSafetyEngine().assess(
        snapshot=snapshot(realized=-100, unrealized=-75),
        maximum_daily_loss=250,
    )

    assert result.total_pnl == -175.0
    assert result.loss_amount == 175.0
    assert result.allowed is True


def test_exact_daily_loss_limit_is_blocked():
    result = DailyLossSafetyEngine().assess(
        snapshot=snapshot(realized=-200, unrealized=-50),
        maximum_daily_loss=250,
    )

    assert result.allowed is False
    assert result.within_limit is False
    assert result.violations == (
        "Maximum daily loss reached: 250.00 >= 250.00.",
    )


def test_loss_over_limit_is_blocked():
    result = DailyLossSafetyEngine().assess(
        snapshot=snapshot(realized=-300, unrealized=25),
        maximum_daily_loss=250,
    )

    assert result.allowed is False
    assert result.loss_amount == 275.0


@pytest.mark.parametrize("value", [0, -1, True, float("inf"), "250"])
def test_maximum_daily_loss_requires_finite_positive_number(value):
    with pytest.raises((TypeError, ValueError)):
        DailyLossSafetyEngine().assess(
            snapshot=snapshot(), maximum_daily_loss=value
        )


def test_unverified_snapshot_type_fails_closed():
    with pytest.raises(TypeError, match="BrokerDailyPnlSnapshot"):
        DailyLossSafetyEngine().assess(
            snapshot=None, maximum_daily_loss=250
        )


def test_snapshot_requires_finite_pnl_and_aware_time():
    with pytest.raises(ValueError, match="finite"):
        snapshot(realized=float("nan"))
    with pytest.raises(ValueError, match="timezone-aware"):
        BrokerDailyPnlSnapshot(
            broker="alpaca-paper",
            realized_pnl=0,
            unrealized_pnl=0,
            observed_at=datetime(2026, 8, 14, 17, 0),
        )


def test_daily_pnl_port_is_runtime_checkable():
    class Source:
        def get_daily_pnl(self):
            return snapshot()

    assert isinstance(Source(), BrokerDailyPnlPort)
