from pathlib import Path

import pytest

from imie.models import ExecutionSafetyPolicy
from imie.runtime import (
    DEFAULT_EXECUTION_RESERVATION_STORE,
    ExecutionSafetyConfig,
)


def test_defaults_are_disabled_and_do_not_grant_execution_limits():
    config = ExecutionSafetyConfig()

    assert config.enabled is False
    assert config.maximum_order_notional is None
    assert config.maximum_risk_amount is None
    assert config.maximum_concurrent_positions is None
    assert config.maximum_position_exposure_age_seconds is None
    assert config.kill_switch_active is False
    assert config.reservation_store_path == Path(
        "runtime/execution/submission_reservations.json"
    )
    assert config.reservation_store_path == DEFAULT_EXECUTION_RESERVATION_STORE


def test_enabled_config_requires_and_normalizes_both_limits():
    config = ExecutionSafetyConfig(
        enabled=True,
        maximum_order_notional=25_000,
        maximum_risk_amount=125,
        reservation_store_path=Path("custom/reservations.json"),
    )

    assert config.maximum_order_notional == 25_000.0
    assert config.maximum_risk_amount == 125.0
    assert config.reservation_store_path == Path("custom/reservations.json")


@pytest.mark.parametrize(
    "overrides, missing",
    [
        ({"maximum_risk_amount": 125}, "maximum_order_notional"),
        ({"maximum_order_notional": 25_000}, "maximum_risk_amount"),
    ],
)
def test_enabled_config_fails_closed_when_a_limit_is_absent(
    overrides, missing
):
    with pytest.raises(ValueError, match=missing):
        ExecutionSafetyConfig(enabled=True, **overrides)


@pytest.mark.parametrize(
    "field, value",
    [
        ("maximum_order_notional", 0),
        ("maximum_order_notional", -1),
        ("maximum_order_notional", float("inf")),
        ("maximum_risk_amount", 0),
        ("maximum_risk_amount", True),
    ],
)
def test_config_rejects_invalid_limits_even_while_disabled(field, value):
    with pytest.raises((TypeError, ValueError)):
        ExecutionSafetyConfig(**{field: value})


def test_reservation_store_path_must_be_path():
    with pytest.raises(TypeError, match="reservation_store_path"):
        ExecutionSafetyConfig(
            reservation_store_path="runtime/reservations.json"
        )


def test_disabled_config_cannot_build_policy():
    with pytest.raises(RuntimeError, match="must be enabled"):
        ExecutionSafetyConfig().build_policy()


def test_enabled_config_builds_typed_financial_policy():
    policy = ExecutionSafetyConfig(
        enabled=True,
        maximum_order_notional=25_000,
        maximum_risk_amount=125,
    ).build_policy()

    assert isinstance(policy, ExecutionSafetyPolicy)
    assert policy.maximum_order_notional == 25_000.0
    assert policy.maximum_risk_amount == 125.0
    assert policy.kill_switch_active is False


def test_enabled_config_builds_active_kill_switch_policy():
    policy = ExecutionSafetyConfig(
        enabled=True,
        maximum_order_notional=25_000,
        maximum_risk_amount=125,
        kill_switch_active=True,
    ).build_policy()

    assert policy.kill_switch_active is True


def test_kill_switch_requires_execution_safety():
    with pytest.raises(ValueError, match="requires execution safety"):
        ExecutionSafetyConfig(kill_switch_active=True)


def test_kill_switch_must_be_bool():
    with pytest.raises(TypeError, match="kill_switch_active"):
        ExecutionSafetyConfig(kill_switch_active=1)


def test_enabled_config_accepts_maximum_concurrent_positions():
    config = ExecutionSafetyConfig(
        enabled=True,
        maximum_order_notional=25_000,
        maximum_risk_amount=125,
        maximum_concurrent_positions=3,
    )

    assert config.maximum_concurrent_positions == 3


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "3"])
def test_maximum_concurrent_positions_requires_positive_int(value):
    with pytest.raises((TypeError, ValueError)):
        ExecutionSafetyConfig(
            enabled=True,
            maximum_order_notional=25_000,
            maximum_risk_amount=125,
            maximum_concurrent_positions=value,
        )


def test_maximum_concurrent_positions_requires_execution_safety():
    with pytest.raises(ValueError, match="requires execution safety"):
        ExecutionSafetyConfig(maximum_concurrent_positions=3)


def test_config_accepts_position_exposure_maximum_age():
    config = ExecutionSafetyConfig(
        enabled=True,
        maximum_order_notional=25_000,
        maximum_risk_amount=125,
        maximum_concurrent_positions=3,
        maximum_position_exposure_age_seconds=5,
    )

    assert config.maximum_position_exposure_age_seconds == 5.0


@pytest.mark.parametrize("value", [0, -1, True, float("inf")])
def test_position_exposure_maximum_age_must_be_positive(value):
    with pytest.raises((TypeError, ValueError)):
        ExecutionSafetyConfig(
            enabled=True,
            maximum_order_notional=25_000,
            maximum_risk_amount=125,
            maximum_concurrent_positions=3,
            maximum_position_exposure_age_seconds=value,
        )


def test_position_exposure_age_requires_concurrent_limit():
    with pytest.raises(ValueError, match="requires maximum_concurrent"):
        ExecutionSafetyConfig(
            enabled=True,
            maximum_order_notional=25_000,
            maximum_risk_amount=125,
            maximum_position_exposure_age_seconds=5,
        )
