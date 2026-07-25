from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from imie.analysts import (
    ParticipationAnalyst,
)
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    MarketBar,
    MarketPhaseType,
    ParticipationAnalysis,
    PressureAnalysis,
)
from tests.test_structure_analyst import (
    create_context,
)


def make_bar(
    *,
    index: int,
    volume: int,
) -> MarketBar:
    return MarketBar(
        symbol="NVDA",
        timestamp=(
            datetime(2026, 7, 16, 9, 30)
            + timedelta(minutes=index * 2)
        ),
        open=100.0,
        high=101.0,
        low=99.5,
        close=100.5,
        volume=volume,
        timeframe="2m",
        provider="test",
    )


def with_volumes(
    volumes: tuple[int, ...],
):
    context = create_context()

    bars = tuple(
        make_bar(
            index=index,
            volume=volume,
        )
        for index, volume in enumerate(volumes)
    )

    return replace(
        context,
        snapshot=replace(
            context.snapshot,
            bars=bars,
        ),
    )


def make_pressure(
    direction: InstitutionalDirection,
) -> AnalystResult:
    if (
        direction
        is InstitutionalDirection.BULLISH
    ):
        pressure = "BUYING"
        opinion = "Buying pressure dominates."
    elif (
        direction
        is InstitutionalDirection.BEARISH
    ):
        pressure = "SELLING"
        opinion = "Selling pressure dominates."
    else:
        pressure = "BALANCED"
        opinion = (
            "Buying and selling pressure remain balanced."
        )

    return AnalystResult(
        analyst="PressureAnalyst",
        analyst_id="PRESSURE",
        opinion=opinion,
        confidence=80.0,
        evidence=[],
        warnings=[],
        payload=PressureAnalysis(
            direction=direction,
            pressure=pressure,
            market_phase=MarketPhaseType.EXPANSION,
            bullish_score=50.0,
            bearish_score=10.0,
            evaluated_bar_count=5,
            directional_bar_count=4,
            confidence=80.0,
            opinion=opinion,
        ),
        enabled=True,
    )


def test_strong_volume_supports_buyers() -> None:
    volumes = (
        *(100_000 for _ in range(15)),
        *(200_000 for _ in range(5)),
    )

    result = ParticipationAnalyst().analyze(
        context=with_volumes(volumes),
        pressure_result=make_pressure(
            InstitutionalDirection.BULLISH
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.participation == "BULLISH"
    assert (
        result.market_phase
        is MarketPhaseType.EXPANSION
    )


def test_strong_volume_supports_sellers() -> None:
    volumes = (
        *(100_000 for _ in range(15)),
        *(200_000 for _ in range(5)),
    )

    result = ParticipationAnalyst().analyze(
        context=with_volumes(volumes),
        pressure_result=make_pressure(
            InstitutionalDirection.BEARISH
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BEARISH
    )
    assert result.participation == "BEARISH"


def test_strong_volume_without_direction_is_neutral() -> None:
    volumes = (
        *(100_000 for _ in range(15)),
        *(200_000 for _ in range(5)),
    )

    result = ParticipationAnalyst().analyze(
        context=with_volumes(volumes),
        pressure_result=make_pressure(
            InstitutionalDirection.NEUTRAL
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.NEUTRAL
    )
    assert (
        result.participation
        == "STRONG_NON_DIRECTIONAL"
    )


def test_weak_volume_is_non_directional() -> None:
    volumes = (
        *(200_000 for _ in range(15)),
        *(50_000 for _ in range(5)),
    )

    result = ParticipationAnalyst().analyze(
        context=with_volumes(volumes),
        pressure_result=make_pressure(
            InstitutionalDirection.BULLISH
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.NEUTRAL
    )
    assert result.participation == "WEAK"
    assert (
        result.market_phase
        is MarketPhaseType.COMPRESSION
    )


def test_analyze_result_wraps_payload() -> None:
    volumes = (
        *(100_000 for _ in range(15)),
        *(200_000 for _ in range(5)),
    )

    result = ParticipationAnalyst().analyze_result(
        context=with_volumes(volumes),
        pressure_result=make_pressure(
            InstitutionalDirection.BULLISH
        ),
    )

    assert result.analyst_id == "PARTICIPATION"
    assert isinstance(
        result.payload,
        ParticipationAnalysis,
    )