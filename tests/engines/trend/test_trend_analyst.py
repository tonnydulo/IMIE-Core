from dataclasses import replace

from imie.engines.trend import TrendAnalyst
from imie.models import (
    MarketObservations,
    MarketPhaseType,
)
from imie.utils.constants import (
    TREND_BEARISH,
    TREND_BULLISH,
    TREND_NEUTRAL,
)
from tests.test_structure_analyst import (
    create_context,
)


def make_context(
    *,
    price_above_ema9: bool = False,
    price_below_ema9: bool = False,
    price_above_vwap: bool = False,
    price_below_vwap: bool = False,
    ema9_rising: bool = False,
    ema9_falling: bool = False,
):
    context = create_context()

    observations = MarketObservations(
        price_above_ema9=price_above_ema9,
        price_below_ema9=price_below_ema9,
        price_above_vwap=price_above_vwap,
        price_below_vwap=price_below_vwap,
        ema9_rising=ema9_rising,
        ema9_falling=ema9_falling,
    )

    return replace(
        context,
        observations=observations,
    )


def test_bullish_trend_resolves_markup_phase() -> None:
    result = TrendAnalyst().analyze(
        make_context(
            price_above_ema9=True,
            price_above_vwap=True,
            ema9_rising=True,
        )
    )

    assert result.opinion == TREND_BULLISH
    assert result.confidence == 100.0
    assert (
        result.payload["market_phase"]
        is MarketPhaseType.MARKUP
    )


def test_bearish_trend_resolves_markdown_phase() -> None:
    result = TrendAnalyst().analyze(
        make_context(
            price_below_ema9=True,
            price_below_vwap=True,
            ema9_falling=True,
        )
    )

    assert result.opinion == TREND_BEARISH
    assert result.confidence == 100.0
    assert (
        result.payload["market_phase"]
        is MarketPhaseType.MARKDOWN
    )


def test_neutral_trend_resolves_compression_phase() -> None:
    result = TrendAnalyst().analyze(
        make_context()
    )

    assert result.opinion == TREND_NEUTRAL
    assert result.confidence == 0.0
    assert (
        result.payload["market_phase"]
        is MarketPhaseType.COMPRESSION
    )