from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.directors.institutional_bias_config import (
    InstitutionalBiasConfig,
)


def test_default_weights() -> None:
    config = InstitutionalBiasConfig()

    assert config.trend_weight == 25.0
    assert config.structure_weight == 20.0
    assert config.liquidity_weight == 15.0
    assert config.order_block_weight == 15.0
    assert config.auction_weight == 10.0
    assert config.pressure_weight == 5.0
    assert config.participation_weight == 5.0
    assert config.value_weight == 5.0


def test_default_thresholds() -> None:
    config = InstitutionalBiasConfig()

    assert config.minimum_directional_spread == 5.0
    assert config.minimum_bias_confidence == 40.0


def test_total_weight() -> None:
    config = InstitutionalBiasConfig()

    assert config.total_weight == 100.0


def test_core_weight() -> None:
    config = InstitutionalBiasConfig()

    assert config.core_weight == 75.0


def test_extended_weight() -> None:
    config = InstitutionalBiasConfig()

    assert config.extended_weight == 25.0


def test_core_and_extended_weights_total_one_hundred() -> None:
    config = InstitutionalBiasConfig()

    assert (
        config.core_weight
        + config.extended_weight
        == 100.0
    )


def test_weights_mapping() -> None:
    config = InstitutionalBiasConfig()

    assert config.weights == {
        "TREND": 25.0,
        "STRUCTURE": 20.0,
        "LIQUIDITY": 15.0,
        "ORDER_BLOCK": 15.0,
        "AUCTION": 10.0,
        "PRESSURE": 5.0,
        "PARTICIPATION": 5.0,
        "VALUE": 5.0,
    }


def test_weights_returns_new_mapping() -> None:
    config = InstitutionalBiasConfig()

    first = config.weights
    second = config.weights

    assert first == second
    assert first is not second


def test_domains() -> None:
    config = InstitutionalBiasConfig()

    assert config.domains == (
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    )


@pytest.mark.parametrize(
    (
        "domain",
        "expected",
    ),
    [
        (
            "TREND",
            25.0,
        ),
        (
            "STRUCTURE",
            20.0,
        ),
        (
            "LIQUIDITY",
            15.0,
        ),
        (
            "ORDER_BLOCK",
            15.0,
        ),
        (
            "AUCTION",
            10.0,
        ),
        (
            "PRESSURE",
            5.0,
        ),
        (
            "PARTICIPATION",
            5.0,
        ),
        (
            "VALUE",
            5.0,
        ),
    ],
)
def test_weight_for(
    domain: str,
    expected: float,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.weight_for(
        domain
    ) == expected


@pytest.mark.parametrize(
    "domain",
    [
        "trend",
        " Trend ",
        "TrEnD",
    ],
)
def test_weight_for_normalizes_domain(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.weight_for(
        domain
    ) == 25.0


@pytest.mark.parametrize(
    "domain",
    [
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
    ],
)
def test_core_domains(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.is_core_domain(
        domain
    ) is True

    assert config.is_extended_domain(
        domain
    ) is False


@pytest.mark.parametrize(
    "domain",
    [
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
def test_extended_domains(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.is_extended_domain(
        domain
    ) is True

    assert config.is_core_domain(
        domain
    ) is False


@pytest.mark.parametrize(
    "domain",
    [
        "trend",
        " Trend ",
        "structure",
        "liquidity",
        "order_block",
    ],
)
def test_core_domain_normalization(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.is_core_domain(
        domain
    ) is True


@pytest.mark.parametrize(
    "domain",
    [
        "auction",
        " pressure ",
        "Participation",
        "value",
    ],
)
def test_extended_domain_normalization(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.is_extended_domain(
        domain
    ) is True


@pytest.mark.parametrize(
    "domain",
    [
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
def test_default_domains_have_weight(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    assert config.has_weight(
        domain
    ) is True


def test_zero_weight_domain_has_no_weight() -> None:
    config = InstitutionalBiasConfig(
        trend_weight=30.0,
        structure_weight=20.0,
        liquidity_weight=15.0,
        order_block_weight=15.0,
        auction_weight=10.0,
        pressure_weight=5.0,
        participation_weight=5.0,
        value_weight=0.0,
    )

    assert config.has_weight(
        "VALUE"
    ) is False


def test_custom_weights() -> None:
    config = InstitutionalBiasConfig(
        trend_weight=30.0,
        structure_weight=20.0,
        liquidity_weight=15.0,
        order_block_weight=10.0,
        auction_weight=10.0,
        pressure_weight=5.0,
        participation_weight=5.0,
        value_weight=5.0,
    )

    assert config.total_weight == 100.0
    assert config.trend_weight == 30.0
    assert config.order_block_weight == 10.0


def test_custom_thresholds() -> None:
    config = InstitutionalBiasConfig(
        minimum_directional_spread=10.0,
        minimum_bias_confidence=55.0,
    )

    assert config.minimum_directional_spread == 10.0
    assert config.minimum_bias_confidence == 55.0


def test_numeric_values_are_rounded() -> None:
    config = InstitutionalBiasConfig(
        trend_weight=25.004,
        structure_weight=19.996,
        liquidity_weight=15.0,
        order_block_weight=15.0,
        auction_weight=10.0,
        pressure_weight=5.0,
        participation_weight=5.0,
        value_weight=5.0,
        minimum_directional_spread=5.004,
        minimum_bias_confidence=39.996,
    )

    assert config.trend_weight == 25.0
    assert config.structure_weight == 20.0
    assert config.minimum_directional_spread == 5.0
    assert config.minimum_bias_confidence == 40.0
    assert config.total_weight == 100.0


def test_config_is_frozen() -> None:
    config = InstitutionalBiasConfig()

    with pytest.raises(
        FrozenInstanceError
    ):
        config.trend_weight = 50.0  # type: ignore[misc]


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "trend_weight",
            -0.01,
        ),
        (
            "structure_weight",
            100.01,
        ),
        (
            "liquidity_weight",
            -0.01,
        ),
        (
            "order_block_weight",
            100.01,
        ),
        (
            "auction_weight",
            -0.01,
        ),
        (
            "pressure_weight",
            100.01,
        ),
        (
            "participation_weight",
            -0.01,
        ),
        (
            "value_weight",
            100.01,
        ),
        (
            "minimum_directional_spread",
            -0.01,
        ),
        (
            "minimum_directional_spread",
            100.01,
        ),
        (
            "minimum_bias_confidence",
            -0.01,
        ),
        (
            "minimum_bias_confidence",
            100.01,
        ),
    ],
)
def test_rejects_values_outside_range(
    field_name: str,
    value: float,
) -> None:
    arguments: dict[str, object] = {
        "trend_weight": 25.0,
        "structure_weight": 20.0,
        "liquidity_weight": 15.0,
        "order_block_weight": 15.0,
        "auction_weight": 10.0,
        "pressure_weight": 5.0,
        "participation_weight": 5.0,
        "value_weight": 5.0,
        "minimum_directional_spread": 5.0,
        "minimum_bias_confidence": 40.0,
    }

    arguments[
        field_name
    ] = value

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be between 0 and 100"
        ),
    ):
        InstitutionalBiasConfig(
            **arguments,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "trend_weight",
        "structure_weight",
        "liquidity_weight",
        "order_block_weight",
        "auction_weight",
        "pressure_weight",
        "participation_weight",
        "value_weight",
        "minimum_directional_spread",
        "minimum_bias_confidence",
    ],
)
def test_rejects_boolean_values(
    field_name: str,
) -> None:
    arguments: dict[str, object] = {
        "trend_weight": 25.0,
        "structure_weight": 20.0,
        "liquidity_weight": 15.0,
        "order_block_weight": 15.0,
        "auction_weight": 10.0,
        "pressure_weight": 5.0,
        "participation_weight": 5.0,
        "value_weight": 5.0,
        "minimum_directional_spread": 5.0,
        "minimum_bias_confidence": 40.0,
    }

    arguments[
        field_name
    ] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be numeric",
    ):
        InstitutionalBiasConfig(
            **arguments,  # type: ignore[arg-type]
        )


def test_rejects_total_below_one_hundred() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Institutional bias weights must total 100"
        ),
    ):
        InstitutionalBiasConfig(
            trend_weight=20.0,
        )


def test_rejects_total_above_one_hundred() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Institutional bias weights must total 100"
        ),
    ):
        InstitutionalBiasConfig(
            trend_weight=30.0,
        )


def test_weight_for_rejects_non_string() -> None:
    config = InstitutionalBiasConfig()

    with pytest.raises(
        TypeError,
        match="domain must be a string",
    ):
        config.weight_for(
            123  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "domain",
    [
        "",
        " ",
    ],
)
def test_weight_for_rejects_empty_domain(
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    with pytest.raises(
        ValueError,
        match="domain cannot be empty",
    ):
        config.weight_for(
            domain
        )


def test_weight_for_rejects_unknown_domain() -> None:
    config = InstitutionalBiasConfig()

    with pytest.raises(
        KeyError,
        match=(
            "Unknown institutional bias domain: UNKNOWN"
        ),
    ):
        config.weight_for(
            "UNKNOWN"
        )


@pytest.mark.parametrize(
    "method_name",
    [
        "is_core_domain",
        "is_extended_domain",
        "has_weight",
    ],
)
def test_domain_helpers_reject_non_string(
    method_name: str,
) -> None:
    config = InstitutionalBiasConfig()

    method = getattr(
        config,
        method_name,
    )

    with pytest.raises(
        TypeError,
        match="domain must be a string",
    ):
        method(
            123
        )


@pytest.mark.parametrize(
    "method_name",
    [
        "is_core_domain",
        "is_extended_domain",
        "has_weight",
    ],
)
@pytest.mark.parametrize(
    "domain",
    [
        "",
        " ",
    ],
)
def test_domain_helpers_reject_empty_domain(
    method_name: str,
    domain: str,
) -> None:
    config = InstitutionalBiasConfig()

    method = getattr(
        config,
        method_name,
    )

    with pytest.raises(
        ValueError,
        match="domain cannot be empty",
    ):
        method(
            domain
        )


def test_unknown_domain_is_not_core() -> None:
    config = InstitutionalBiasConfig()

    assert config.is_core_domain(
        "UNKNOWN"
    ) is False


def test_unknown_domain_is_not_extended() -> None:
    config = InstitutionalBiasConfig()

    assert config.is_extended_domain(
        "UNKNOWN"
    ) is False


def test_unknown_domain_has_no_weight() -> None:
    config = InstitutionalBiasConfig()

    assert config.has_weight(
        "UNKNOWN"
    ) is False