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
