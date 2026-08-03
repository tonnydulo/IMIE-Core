from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from imie.analysts import (
    PressureAnalyst,
)
from imie.models import (
    InstitutionalDirection,
    MarketBar,
    MarketPhaseType,
    PressureAnalysis,
)
from tests.test_structure_analyst import (
    create_context,
)


def make_bar(
    *,
    index: int,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> MarketBar:
    return MarketBar(
        symbol="NVDA",
        timestamp=(
            datetime(2026, 7, 16, 9, 30)
            + timedelta(minutes=index * 2)
        ),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=100_000,
        timeframe="2m",
        provider="test",
    )


def with_bars(
    bars: tuple[MarketBar, ...],
):
    context = create_context()

    snapshot = replace(
        context.snapshot,
        bars=bars,
    )

    return replace(
        context,
        snapshot=snapshot,
    )


def test_buying_pressure_dominates() -> None:
    bars = tuple(
        make_bar(
            index=index,
            open_price=100.0 + index,
            high=101.1 + index,
            low=99.8 + index,
            close=101.0 + index,
        )
        for index in range(5)
    )

    result = PressureAnalyst().analyze(
        with_bars(bars)
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.pressure == "BUYING"
    assert (
        result.market_phase
        is MarketPhaseType.EXPANSION
    )


def test_selling_pressure_dominates() -> None:
    bars = tuple(
        make_bar(
            index=index,
            open_price=105.0 - index,
            high=105.2 - index,
            low=103.8 - index,
            close=104.0 - index,
        )
        for index in range(5)
    )

    result = PressureAnalyst().analyze(
        with_bars(bars)
    )

    assert (
        result.direction
        is InstitutionalDirection.BEARISH
    )
    assert result.pressure == "SELLING"
    assert (
        result.market_phase
        is MarketPhaseType.EXPANSION
    )


def test_balanced_pressure() -> None:
    bars = (
        make_bar(
            index=0,
            open_price=100.0,
            high=101.1,
            low=99.8,
            close=101.0,
        ),
        make_bar(
            index=1,
            open_price=101.0,
            high=101.2,
            low=99.8,
            close=100.0,
        ),
        make_bar(
            index=2,
            open_price=100.0,
            high=101.1,
            low=99.8,
            close=101.0,
        ),
        make_bar(
            index=3,
            open_price=101.0,
            high=101.2,
            low=99.8,
            close=100.0,
        ),
    )

    result = PressureAnalyst().analyze(
        with_bars(bars)
    )

    assert (
        result.direction
        is InstitutionalDirection.NEUTRAL
    )
    assert result.pressure == "BALANCED"
    assert (
        result.market_phase
        is MarketPhaseType.COMPRESSION
    )


def test_analyze_result_wraps_pressure_analysis() -> None:
    bars = tuple(
        make_bar(
            index=index,
            open_price=100.0 + index,
            high=101.1 + index,
            low=99.8 + index,
            close=101.0 + index,
        )
        for index in range(5)
    )

    result = PressureAnalyst().analyze_result(
        with_bars(bars)
    )

    assert result.analyst_id == "PRESSURE"
    assert isinstance(
        result.payload,
        PressureAnalysis,
    )


def test_insufficient_bars_returns_unknown() -> None:
    bars = (
        make_bar(
            index=0,
            open_price=100.0,
            high=101.0,
            low=99.5,
            close=100.5,
        ),
    )

    result = PressureAnalyst().analyze(
        with_bars(bars)
    )

    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert (
        result.market_phase
        is MarketPhaseType.UNKNOWN
    )