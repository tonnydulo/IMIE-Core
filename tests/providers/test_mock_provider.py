from imie.providers.mock_provider import (
    MockProvider,
)
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from imie.engines.structure.swing_detector import (
    SwingDetector,
)
from imie.engines.liquidity import (
    EqualHighDetector,
    EqualLowDetector,
)
from imie.engines.structure.core import (
    BosEngine,
)
from imie.engines.order_blocks import (
    OrderBlockDetector,
)
from imie.models import (
    StructureResult,
)

def test_mock_provider_timestamps_are_timezone_aware() -> None:
    provider = MockProvider()

    connected = provider.connect()
    quote = provider.get_quote(
        "NVDA"
    )
    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )
    disconnected = provider.disconnect()

    assert connected.timestamp.tzinfo is not None
    assert quote.timestamp.tzinfo is not None
    assert disconnected.timestamp.tzinfo is not None

    assert bars

    for bar in bars:
        assert bar.timestamp.tzinfo is not None

def test_mock_provider_bars_are_aligned_to_timeframe() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )

    assert len(
        bars
    ) == 3

    for bar in bars:
        assert bar.timestamp.second == 0
        assert bar.timestamp.microsecond == 0
        assert bar.timestamp.minute % 2 == 0


def test_mock_provider_latest_bar_is_recent() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )

    now = datetime.now(
        UTC
    )

    age_seconds = (
        now
        - bars[-1].timestamp
    ).total_seconds()

    assert age_seconds >= 120.0
    assert age_seconds <= 300.0

def test_mock_provider_generates_confirmed_market_swings() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=40,
    )

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    swings = detector.detect(
        bars
    )

    swing_highs = tuple(
        swing
        for swing in swings
        if swing.kind == "HIGH"
    )

    swing_lows = tuple(
        swing
        for swing in swings
        if swing.kind == "LOW"
    )

    assert swing_highs
    assert swing_lows

    assert len(swing_highs) >= 2
    assert len(swing_lows) >= 2

def test_mock_provider_generates_equal_high_and_low_liquidity() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=40,
    )

    swings = SwingDetector(
        left_bars=2,
        right_bars=2,
    ).detect(
        bars
    )

    equal_highs = EqualHighDetector().detect(
        swings
    )

    equal_lows = EqualLowDetector().detect(
        swings
    )

    assert equal_highs
    assert equal_lows

    assert any(
        finding.point.first_index == 4
        and finding.point.second_index == 10
        for finding in equal_highs
    )

    assert any(
        finding.point.first_index == 7
        and finding.point.second_index == 13
        for finding in equal_lows
    )

def test_mock_provider_generates_bullish_bos() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=40,
    )

    swings = SwingDetector(
        left_bars=2,
        right_bars=2,
    ).detect(
        bars
    )

    swing_highs = tuple(
        swing
        for swing in swings
        if swing.kind == "HIGH"
    )

    swing_lows = tuple(
        swing
        for swing in swings
        if swing.kind == "LOW"
    )

    bos = BosEngine().evaluate(
        bars=bars,
        highs=swing_highs,
        lows=swing_lows,
    )

    assert bos.detected is True
    assert bos.bullish_break is True
    assert bos.bearish_break is False

    assert bos.bullish_break_level is not None
    assert bos.confirmation_price is not None

    assert (
        bos.confirmation_price
        > bos.bullish_break_level
    )

def test_mock_provider_generates_bullish_order_block() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=40,
    )

    swings = SwingDetector(
        left_bars=2,
        right_bars=2,
    ).detect(
        bars
    )

    swing_highs = tuple(
        swing
        for swing in swings
        if swing.kind == "HIGH"
    )

    swing_lows = tuple(
        swing
        for swing in swings
        if swing.kind == "LOW"
    )

    bos = BosEngine().evaluate(
        bars=bars,
        highs=swing_highs,
        lows=swing_lows,
    )

    structure = StructureResult(
        symbol="NVDA",
        direction="long",
        state="BULLISH_STRUCTURE",
        confidence=90.0,
        nearest_support=None,
        nearest_resistance=None,
        structural_target=None,
        structural_stop=None,
        projected_reward=None,
        projected_risk=None,
        projected_rr=None,
        swing_high_count=len(
            swing_highs
        ),
        swing_low_count=len(
            swing_lows
        ),
        bullish_break=bos.bullish_break,
        bearish_break=bos.bearish_break,
        bullish_break_level=(
            bos.bullish_break_level
        ),
        bearish_break_level=(
            bos.bearish_break_level
        ),
        break_confirmation_price=(
            bos.confirmation_price
        ),
        bullish_choch=False,
        bearish_choch=False,
        bullish_mss=False,
        bearish_mss=False,
        mss_confidence=0.0,
        mss_reason="",
        evidence=(
            "Mock bullish BOS confirmed.",
        ),
        warnings=(),
        reason=(
            "Mock market structure supports "
            "bullish order-block detection."
        ),
    )

    findings = OrderBlockDetector().detect(
        bars=tuple(
            bars
        ),
        structure=structure,
    )

    assert len(findings) == 1

    finding = findings[0]

    assert finding.source_bar_index == 38
    assert finding.confidence >= 60.0

def test_mock_provider_quote_aligns_with_latest_bar_close() -> None:
    provider = MockProvider()

    quote = provider.get_quote(
        "NVDA"
    )

    for limit in (
        40,
        500,
    ):
        bars = provider.get_bars(
            "NVDA",
            "2m",
            limit=limit,
        )

        assert abs(
            bars[-1].close
            - quote.last
        ) < 1e-9
