from __future__ import annotations

from dataclasses import replace

from imie.analysts import (
    ValueAnalyst,
)
from imie.models import (
    InstitutionalDirection,
    MarketPhaseType,
    ValueAnalysis,
)
from tests.test_structure_analyst import (
    create_context,
)


def make_context(
    *,
    price: float,
    vwap: float | None,
    atr14: float | None = 1.0,
):
    context = create_context()

    measurements = replace(
        context.measurements,
        price=price,
        vwap=vwap,
        atr14=atr14,
        core_tolerance=0.0,
    )

    return replace(
        context,
        measurements=measurements,
    )


def test_discount_value_is_bullish() -> None:
    result = ValueAnalyst().analyze(
        make_context(
            price=99.0,
            vwap=100.0,
            atr14=1.0,
        )
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.value_state == "DISCOUNT"
    assert (
        result.market_phase
        is MarketPhaseType.ACCUMULATION
    )


def test_premium_value_is_bearish() -> None:
    result = ValueAnalyst().analyze(
        make_context(
            price=101.0,
            vwap=100.0,
            atr14=1.0,
        )
    )

    assert (
        result.direction
        is InstitutionalDirection.BEARISH
    )
    assert result.value_state == "PREMIUM"
    assert (
        result.market_phase
        is MarketPhaseType.DISTRIBUTION
    )


def test_near_vwap_is_fair_value() -> None:
    result = ValueAnalyst().analyze(
        make_context(
            price=100.25,
            vwap=100.0,
            atr14=1.0,
        )
    )

    assert (
        result.direction
        is InstitutionalDirection.NEUTRAL
    )
    assert result.value_state == "FAIR_VALUE"
    assert (
        result.market_phase
        is MarketPhaseType.COMPRESSION
    )


def test_missing_vwap_returns_unknown() -> None:
    result = ValueAnalyst().analyze(
        make_context(
            price=100.0,
            vwap=None,
        )
    )

    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.value_state == "UNKNOWN"
    assert (
        result.market_phase
        is MarketPhaseType.UNKNOWN
    )
    assert result.confidence == 0.0


def test_analyze_result_wraps_value_analysis() -> None:
    result = ValueAnalyst().analyze_result(
        make_context(
            price=99.0,
            vwap=100.0,
            atr14=1.0,
        )
    )

    assert result.analyst_id == "VALUE"
    assert isinstance(
        result.payload,
        ValueAnalysis,
    )