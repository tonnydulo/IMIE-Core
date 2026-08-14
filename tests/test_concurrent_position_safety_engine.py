from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    BrokerPositionExposurePort,
    ConcurrentPositionSafetyEngine,
)
from imie.models import (
    BrokerPositionExposure,
    ConcurrentPositionAssessment,
)


NOW = datetime(2026, 8, 14, 15, 0, tzinfo=timezone.utc)


def exposure(*symbols: str) -> BrokerPositionExposure:
    return BrokerPositionExposure(
        broker="alpaca-paper",
        open_symbols=tuple(symbols),
        observed_at=NOW,
    )


def test_new_symbol_is_allowed_below_concurrent_limit():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol="NVDA",
        exposure=exposure("AAPL"),
        maximum_concurrent_positions=2,
    )

    assert isinstance(result, ConcurrentPositionAssessment)
    assert result.allowed is True
    assert result.open_position_count == 1
    assert result.symbol_already_open is False
    assert result.violations == ()


def test_new_symbol_is_blocked_at_concurrent_limit():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol="NVDA",
        exposure=exposure("AAPL", "TSLA"),
        maximum_concurrent_positions=2,
    )

    assert result.allowed is False
    assert result.violations == (
        "Maximum concurrent positions reached: 2 >= 2.",
    )


def test_existing_symbol_is_allowed_at_concurrent_limit():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol=" nvda ",
        exposure=exposure("NVDA", "AAPL"),
        maximum_concurrent_positions=2,
    )

    assert result.allowed is True
    assert result.symbol_already_open is True


def test_fresh_exposure_is_allowed_within_maximum_age():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol="NVDA",
        exposure=exposure("AAPL"),
        maximum_concurrent_positions=2,
        checked_at=NOW + timedelta(seconds=2),
        maximum_exposure_age_seconds=5,
    )

    assert result.allowed is True
    assert result.exposure_fresh is True
    assert result.exposure_age_seconds == 2.0
    assert result.maximum_exposure_age_seconds == 5.0


def test_stale_exposure_blocks_even_below_position_limit():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol="NVDA",
        exposure=exposure("AAPL"),
        maximum_concurrent_positions=2,
        checked_at=NOW + timedelta(seconds=5.001),
        maximum_exposure_age_seconds=5,
    )

    assert result.allowed is False
    assert result.exposure_fresh is False
    assert result.violations == (
        "Broker position exposure is stale: 5.001s > 5.000s.",
    )


def test_exact_exposure_age_boundary_is_fresh():
    result = ConcurrentPositionSafetyEngine().assess(
        symbol="NVDA",
        exposure=exposure(),
        maximum_concurrent_positions=1,
        checked_at=NOW + timedelta(seconds=5),
        maximum_exposure_age_seconds=5,
    )

    assert result.allowed is True
    assert result.exposure_fresh is True


def test_future_dated_exposure_fails_closed():
    with pytest.raises(ValueError, match="future"):
        ConcurrentPositionSafetyEngine().assess(
            symbol="NVDA",
            exposure=exposure(),
            maximum_concurrent_positions=1,
            checked_at=NOW - timedelta(microseconds=1),
            maximum_exposure_age_seconds=5,
        )


def test_exposure_freshness_configuration_must_be_complete():
    with pytest.raises(ValueError, match="configured together"):
        ConcurrentPositionSafetyEngine().assess(
            symbol="NVDA",
            exposure=exposure(),
            maximum_concurrent_positions=1,
            checked_at=NOW,
        )


def test_exposure_normalizes_and_deduplicates_symbols():
    value = exposure(" tsla ", "aapl")

    assert value.broker == "alpaca-paper"
    assert value.open_symbols == ("AAPL", "TSLA")
    assert value.open_position_count == 2
    assert value.contains(" aapl ") is True

    with pytest.raises(ValueError, match="duplicates"):
        exposure("NVDA", "nvda")


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_maximum_concurrent_positions_requires_positive_int(value):
    with pytest.raises((TypeError, ValueError)):
        ConcurrentPositionSafetyEngine().assess(
            symbol="NVDA",
            exposure=exposure(),
            maximum_concurrent_positions=value,
        )


def test_exposure_requires_verified_typed_input():
    with pytest.raises(TypeError, match="exposure"):
        ConcurrentPositionSafetyEngine().assess(
            symbol="NVDA",
            exposure=None,
            maximum_concurrent_positions=2,
        )


def test_exposure_requires_aware_observation_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        BrokerPositionExposure(
            broker="alpaca-paper",
            open_symbols=(),
            observed_at=datetime(2026, 8, 14, 15, 0),
        )


def test_exposure_port_is_broker_neutral_and_runtime_checkable():
    class ExposureSource:
        def get_open_position_exposure(self):
            return exposure("NVDA")

    assert isinstance(ExposureSource(), BrokerPositionExposurePort)
