from __future__ import annotations

from imie.models import (
    AnalystResult,
    AuctionAnalysis,
    LiquidityAnalysis,
    OrderBlockAnalysis,
    PressureAnalysis,
    StructureResult,
    ParticipationAnalysis,
    ValueAnalysis,
)
from imie.services import (
    build_institutional_results,
)
from imie.utils.analyst_ids import (
    ANALYST_AUCTION,
    ANALYST_LIQUIDITY,
    ANALYST_ORDER_BLOCK,
    ANALYST_PRESSURE,
    ANALYST_STRUCTURE,
    ANALYST_PARTICIPATION,
    ANALYST_VALUE,
)
from tests.test_structure_analyst import (
    create_context,
)

def make_trend_result() -> AnalystResult:
    return AnalystResult(
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion="BULLISH",
        confidence=90.0,
        evidence=[
            "Price is above EMA9.",
            "Price is above VWAP.",
        ],
        warnings=[],
        payload=None,
        enabled=True,
    )

def test_builds_all_institutional_results() -> None:
    context = create_context()

    (
        structure_result,
        liquidity_result,
        order_block_result,
        auction_result,
        pressure_result,
        participation_result,
        value_result,
    ) = build_institutional_results(
        context,
        make_trend_result(),
    )

    assert (
        structure_result.analyst_id
        == ANALYST_STRUCTURE
    )
    assert (
        liquidity_result.analyst_id
        == ANALYST_LIQUIDITY
    )
    assert (
        order_block_result.analyst_id
        == ANALYST_ORDER_BLOCK
    )
    assert (
        auction_result.analyst_id
        == ANALYST_AUCTION
    )
    assert (
        pressure_result.analyst_id
        == ANALYST_PRESSURE
    )
    assert (
        participation_result.analyst_id
        == ANALYST_PARTICIPATION
    )

    assert value_result.analyst_id == ANALYST_VALUE

    assert isinstance(
        participation_result.payload,
        ParticipationAnalysis,
    )
    assert isinstance(
        value_result.payload,
        ValueAnalysis,
    )

def test_returns_expected_payload_types() -> None:
    context = create_context()

    (
        structure_result,
        liquidity_result,
        order_block_result,
        auction_result,
        pressure_result,
        participation_result,
        value_result,
    ) = build_institutional_results(
        context,
        make_trend_result(),
    )

    assert isinstance(
        structure_result.payload,
        StructureResult,
    )
    assert isinstance(
        liquidity_result.payload,
        LiquidityAnalysis,
    )
    assert isinstance(
        order_block_result.payload,
        OrderBlockAnalysis,
    )
    assert isinstance(
        auction_result.payload,
        AuctionAnalysis,
    )
    assert isinstance(
        pressure_result.payload,
        PressureAnalysis,
    )


def test_results_are_enabled() -> None:
    context = create_context()

    results = build_institutional_results(
        context,
        make_trend_result(),
    )

    assert all(
        result.enabled
        for result in results
    )