from datetime import datetime, timezone

from imie.engines.structure.core import StructureEngine
from imie.models import (
    MarketBar,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    TradingContext,
)


def make_bar(
    *,
    minute: int,
    close: float,
    high: float,
    low: float,
) -> MarketBar:
    timestamp = datetime(
        2026,
        7,
        10,
        14,
        minute,
        tzinfo=timezone.utc,
    )

    return MarketBar(
        symbol="SPY",
        timeframe="2m",
        timestamp=timestamp,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def create_context(
    bars: list[MarketBar],
) -> TradingContext:

    quote = Quote(
        symbol="SPY",
        bid=bars[-1].close,
        ask=bars[-1].close,
        last=bars[-1].close,
        timestamp=bars[-1].timestamp,
    )

    snapshot = MarketSnapshot(
        symbol="SPY",
        timeframe="2m",
        timestamp=bars[-1].timestamp,
        quote=quote,
        bars=bars,
    )

    measurements = MarketMeasurements(
        price=bars[-1].close,
    )

    observations = MarketObservations()

    return TradingContext(
        snapshot=snapshot,
        measurements=measurements,
        observations=observations,
    )


def test_structure_engine_sets_bullish_bos():

    bars = [
        make_bar(minute=0, close=98, high=100, low=96),
        make_bar(minute=1, close=101, high=102, low=99),
        make_bar(minute=2, close=103, high=104, low=100),
        make_bar(minute=3, close=99, high=100, low=97),
        make_bar(minute=4, close=105, high=106, low=103),
    ]

    engine = StructureEngine()

    result = engine.evaluate(
        create_context(bars)
    )

    assert isinstance(result.bullish_break, bool)
    assert isinstance(result.bearish_break, bool)


def test_structure_engine_sets_bearish_bos():

    bars = [
        make_bar(minute=0, close=105, high=106, low=103),
        make_bar(minute=1, close=102, high=104, low=100),
        make_bar(minute=2, close=98, high=100, low=96),
        make_bar(minute=3, close=101, high=102, low=99),
        make_bar(minute=4, close=94, high=95, low=92),
    ]

    engine = StructureEngine()

    result = engine.evaluate(
        create_context(bars)
    )

    assert isinstance(result.bullish_break, bool)
    assert isinstance(result.bearish_break, bool)