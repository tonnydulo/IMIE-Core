from datetime import datetime, timezone

from imie.engines.structure.core import StructureEngine
from imie.models import (
    BosResult,
    ChochResult,
    MarketBar,
    MarketMeasurements,
    MarketObservations,
    MarketSnapshot,
    Quote,
    Swing,
    TradingContext,
)


class StubSwingDetector:
    def __init__(
        self,
        swings: tuple[Swing, ...],
    ) -> None:
        self.swings = swings

    def detect(
        self,
        bars,
    ) -> tuple[Swing, ...]:
        return self.swings


class StubBosEngine:
    def __init__(
        self,
        result: BosResult,
    ) -> None:
        self.result = result

    def evaluate(
        self,
        *,
        bars,
        highs,
        lows,
    ) -> BosResult:
        return self.result


class StubChochEngine:
    def __init__(
        self,
        result: ChochResult,
    ) -> None:
        self.result = result

    def evaluate(
        self,
        *,
        structure_direction: str,
        bullish_break: bool,
        bearish_break: bool,
    ) -> ChochResult:
        return self.result


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
    *,
    price: float,
) -> TradingContext:
    bars = [
        make_bar(
            minute=0,
            close=price,
            high=price + 1.0,
            low=price - 1.0,
        )
    ]

    quote = Quote(
        symbol="SPY",
        bid=price,
        ask=price,
        last=price,
        timestamp=bars[-1].timestamp,
    )

    snapshot = MarketSnapshot(
        symbol="SPY",
        timeframe="2m",
        timestamp=bars[-1].timestamp,
        quote=quote,
        bars=bars,
    )

    return TradingContext(
        snapshot=snapshot,
        measurements=MarketMeasurements(
            price=price,
        ),
        observations=MarketObservations(),
    )


def test_structure_engine_carries_bullish_choch():
    engine = StructureEngine()

    engine.detector = StubSwingDetector(
        swings=(
            Swing(
                index=1,
                price=110.0,
                kind="HIGH",
                strength=2,
            ),
            Swing(
                index=3,
                price=105.0,
                kind="HIGH",
                strength=2,
            ),
            Swing(
                index=2,
                price=100.0,
                kind="LOW",
                strength=2,
            ),
            Swing(
                index=4,
                price=95.0,
                kind="LOW",
                strength=2,
            ),
        )
    )

    engine.bos_engine = StubBosEngine(
        BosResult(
            bullish_break=True,
            bullish_break_level=105.0,
            confirmation_price=106.0,
        )
    )

    engine.choch_engine = StubChochEngine(
        ChochResult(
            bullish_choch=True,
            bearish_choch=False,
        )
    )

    result = engine.evaluate(
        create_context(price=106.0)
    )

    assert result.direction == "short"
    assert result.bullish_break is True
    assert result.bearish_break is False
    assert result.bullish_choch is True
    assert result.bearish_choch is False
    assert "sellers to buyers" in result.reason.lower()

    assert any(
        "bullish change of character" in item.lower()
        for item in result.evidence
    )


def test_structure_engine_carries_bearish_choch():
    engine = StructureEngine()

    engine.detector = StubSwingDetector(
        swings=(
            Swing(
                index=1,
                price=100.0,
                kind="HIGH",
                strength=2,
            ),
            Swing(
                index=3,
                price=105.0,
                kind="HIGH",
                strength=2,
            ),
            Swing(
                index=2,
                price=90.0,
                kind="LOW",
                strength=2,
            ),
            Swing(
                index=4,
                price=95.0,
                kind="LOW",
                strength=2,
            ),
        )
    )

    engine.bos_engine = StubBosEngine(
        BosResult(
            bearish_break=True,
            bearish_break_level=95.0,
            confirmation_price=94.0,
        )
    )

    engine.choch_engine = StubChochEngine(
        ChochResult(
            bullish_choch=False,
            bearish_choch=True,
        )
    )

    result = engine.evaluate(
        create_context(price=94.0)
    )

    assert result.direction == "long"
    assert result.bullish_break is False
    assert result.bearish_break is True
    assert result.bullish_choch is False
    assert result.bearish_choch is True
    assert "buyers to sellers" in result.reason.lower()

    assert any(
        "bearish change of character" in item.lower()
        for item in result.evidence
    )