from dataclasses import replace

import pytest

from imie.directors.market_phase_config import (
    MarketPhaseConfig,
)


def test_default_weights_total_100() -> None:
    config = MarketPhaseConfig()

    total = (
        config.structure_weight
        + config.auction_weight
        + config.liquidity_weight
        + config.pressure_weight
        + config.participation_weight
        + config.order_block_weight
        + config.trend_weight
        + config.value_weight
    )

    assert total == 100.0


def test_weight_lookup() -> None:
    config = MarketPhaseConfig()

    assert config.weight_for("STRUCTURE") == 25.0
    assert config.weight_for("AUCTION") == 20.0
    assert config.weight_for("LIQUIDITY") == 15.0
    assert config.weight_for("PRESSURE") == 10.0
    assert config.weight_for("PARTICIPATION") == 10.0
    assert config.weight_for("ORDER_BLOCK") == 10.0
    assert config.weight_for("TREND") == 5.0
    assert config.weight_for("VALUE") == 5.0


def test_unknown_domain_raises() -> None:
    config = MarketPhaseConfig()

    with pytest.raises(ValueError):
        config.weight_for("INVALID")


def test_invalid_total_weight_raises() -> None:
    with pytest.raises(ValueError):
        replace(
            MarketPhaseConfig(),
            value_weight=10.0,
        )


def test_negative_weight_raises() -> None:
    with pytest.raises(ValueError):
        replace(
            MarketPhaseConfig(),
            trend_weight=-1.0,
        )


def test_invalid_confidence_raises() -> None:
    with pytest.raises(ValueError):
        replace(
            MarketPhaseConfig(),
            minimum_phase_confidence=150.0,
        )


def test_invalid_agreement_raises() -> None:
    with pytest.raises(ValueError):
        replace(
            MarketPhaseConfig(),
            minimum_phase_agreement=0,
        )