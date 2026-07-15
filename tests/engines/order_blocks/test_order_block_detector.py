
from __future__ import annotations

import pytest

from imie.engines.order_blocks import OrderBlockDetector
from imie.models import (
    MarketBar,
    OrderBlockFinding,
    OrderBlockOrigin,
    OrderBlockSide,
    StructureResult,
)


def make_bar(
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
    timestamp: int = 1,
) -> MarketBar:
    return MarketBar(
        symbol="SPY",
        timeframe="1m",
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def make_source_bar(
    *,
    open_price: float = 550.00,
    high: float = 550.10,
    low: float = 549.50,
    close: float = 549.80,
    timestamp: int = 1,
) -> MarketBar:
    """
    Default bearish source candle.

    Body:
        550.00 - 549.80 = 0.20
    """
    return make_bar(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
        timestamp=timestamp,
    )


def make_displacement_bar(
    *,
    open_price: float = 549.75,
    high: float = 550.70,
    low: float = 549.70,
    close: float = 550.60,
    timestamp: int = 2,
) -> MarketBar:
    """
    Default bullish displacement candle.

    Body:
        550.60 - 549.75 = 0.85

    Range:
        550.70 - 549.70 = 1.00

    Body ratio:
        0.85 / 1.00 = 0.85

    Expansion multiple relative to default source:
        0.85 / 0.20 = 4.25

    Close location:
        (550.60 - 549.70) / 1.00 = 0.90
    """
    return make_bar(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
        timestamp=timestamp,
    )


def make_structure(
    *,
    direction: str = "long",
    bullish_break: bool = True,
    bullish_choch: bool = False,
    bullish_mss: bool = False,
) -> StructureResult:
    """
    Build a valid StructureResult for BOS, CHoCH, MSS,
    or no-confirmation test scenarios.

    StructureResult validation requires:

    - bullish CHoCH requires bullish break;
    - bullish MSS requires bullish CHoCH;
    - any confirmed break requires a break level;
    - any confirmed break requires a completed close.
    """
    has_break = (
        bullish_break
        or bullish_choch
        or bullish_mss
    )

    return StructureResult(
        symbol="SPY",
        direction=direction,
        state=(
            "BULLISH_MSS"
            if bullish_mss
            else "BULLISH_CHOCH"
            if bullish_choch
            else "BULLISH_STRUCTURE"
            if bullish_break
            else "NEUTRAL_STRUCTURE"
        ),
        confidence=90.0 if has_break else 50.0,
        nearest_support=549.50,
        nearest_resistance=552.00,
        structural_target=552.00,
        structural_stop=549.00,
        projected_reward=1.40,
        projected_risk=0.60,
        projected_rr=2.33,
        swing_high_count=3,
        swing_low_count=3,
        bullish_break=has_break,
        bearish_break=False,
        bullish_break_level=550.10 if has_break else None,
        bearish_break_level=None,
        break_confirmation_price=550.60 if has_break else None,
        bullish_choch=bullish_choch,
        bearish_choch=False,
        bullish_mss=bullish_mss,
        bearish_mss=False,
        mss_confidence=95.0 if bullish_mss else 0.0,
        mss_reason=(
            "Bullish market structure shift confirmed."
            if bullish_mss
            else ""
        ),
        evidence=(
            "Completed bullish structural confirmation.",
        ) if has_break else (
            "No completed bullish structural confirmation.",
        ),
        warnings=(),
        reason=(
            "Bullish structure confirmed."
            if has_break
            else "Structure remains unconfirmed."
        ),
    )


def detect_default(
    *,
    detector: OrderBlockDetector | None = None,
    source: MarketBar | None = None,
    displacement: MarketBar | None = None,
    structure: StructureResult | None = None,
) -> tuple[OrderBlockFinding, ...]:
    active_detector = detector or OrderBlockDetector()

    return active_detector.detect(
        bars=(
            source or make_source_bar(),
            displacement or make_displacement_bar(),
        ),
        structure=structure or make_structure(),
    )


def test_fewer_than_two_bars_returns_empty() -> None:
    detector = OrderBlockDetector()

    result = detector.detect(
        bars=(make_source_bar(),),
        structure=make_structure(),
    )

    assert result == ()


def test_bearish_source_displacement_and_bos_create_finding() -> None:
    result = detect_default()

    assert len(result) == 1
    assert isinstance(
        result[0],
        OrderBlockFinding,
    )


def test_bullish_source_is_rejected() -> None:
    bullish_source = make_source_bar(
        open_price=549.80,
        high=550.10,
        low=549.50,
        close=550.00,
    )

    result = detect_default(
        source=bullish_source,
    )

    assert result == ()


def test_bearish_displacement_candle_is_rejected() -> None:
    bearish_displacement = make_displacement_bar(
        open_price=550.60,
        high=550.70,
        low=549.70,
        close=549.80,
    )

    result = detect_default(
        displacement=bearish_displacement,
    )

    assert result == ()


def test_weak_body_ratio_is_rejected() -> None:
    """
    Large total range with a relatively small body.

    Body:
        550.20 - 549.90 = 0.30

    Range:
        550.80 - 549.60 = 1.20

    Body ratio:
        0.25, below the default 0.60 threshold.
    """
    weak_body_ratio = make_displacement_bar(
        open_price=549.90,
        high=550.80,
        low=549.60,
        close=550.20,
    )

    result = detect_default(
        displacement=weak_body_ratio,
    )

    assert result == ()


def test_insufficient_body_expansion_is_rejected() -> None:
    """
    Source body:
        550.00 - 549.60 = 0.40

    Displacement body:
        550.30 - 549.80 = 0.50

    Expansion:
        0.50 / 0.40 = 1.25, below the default 1.50.
    """
    larger_source = make_source_bar(
        open_price=550.00,
        high=550.10,
        low=549.50,
        close=549.60,
    )

    insufficient_expansion = make_displacement_bar(
        open_price=549.80,
        high=550.35,
        low=549.75,
        close=550.30,
    )

    result = detect_default(
        source=larger_source,
        displacement=insufficient_expansion,
    )

    assert result == ()


def test_weak_close_location_is_rejected() -> None:
    """
    The candle has a sufficient bullish body but closes too far
    from its high.

    Range:
        551.00 - 549.50 = 1.50

    Close location:
        (550.20 - 549.50) / 1.50 = 0.4667,
        below the default 0.70 threshold.
    """
    weak_close = make_displacement_bar(
        open_price=549.60,
        high=551.00,
        low=549.50,
        close=550.20,
    )

    result = detect_default(
        displacement=weak_close,
    )

    assert result == ()


def test_close_below_source_high_is_rejected() -> None:
    """
    The displacement candle qualifies internally but does not
    close above the source candle high of 550.10.
    """
    below_source_high = make_displacement_bar(
        open_price=549.50,
        high=550.15,
        low=549.45,
        close=550.05,
    )

    result = detect_default(
        displacement=below_source_high,
    )

    assert result == ()


def test_no_bullish_structure_confirmation_returns_empty() -> None:
    no_confirmation = make_structure(
        direction="neutral",
        bullish_break=False,
        bullish_choch=False,
        bullish_mss=False,
    )

    result = detect_default(
        structure=no_confirmation,
    )

    assert result == ()


def test_finding_uses_source_candle_range() -> None:
    source = make_source_bar(
        high=550.25,
        low=549.35,
    )

    result = detect_default(
        source=source,
    )

    finding = result[0]

    assert finding.upper == 550.25
    assert finding.lower == 549.35


def test_finding_side_is_bullish() -> None:
    result = detect_default()

    assert (
        result[0].side
        is OrderBlockSide.BULLISH
    )


def test_origin_resolves_bos() -> None:
    result = detect_default(
        structure=make_structure(
            bullish_break=True,
            bullish_choch=False,
            bullish_mss=False,
        ),
    )

    assert (
        result[0].origin
        is OrderBlockOrigin.BOS
    )


def test_origin_resolves_choch() -> None:
    result = detect_default(
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=False,
        ),
    )

    assert (
        result[0].origin
        is OrderBlockOrigin.CHOCH
    )


def test_origin_resolves_mss() -> None:
    result = detect_default(
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=True,
        ),
    )

    assert (
        result[0].origin
        is OrderBlockOrigin.MSS
    )


def test_invalid_bar_input_is_rejected() -> None:
    detector = OrderBlockDetector()

    with pytest.raises(
        TypeError,
        match="bars must contain MarketBar objects",
    ):
        detector.detect(
            bars=(
                make_source_bar(),
                None,  # type: ignore[arg-type]
            ),
            structure=make_structure(),
        )


def test_invalid_structure_result_is_rejected() -> None:
    detector = OrderBlockDetector()

    with pytest.raises(
        TypeError,
        match="structure must be a StructureResult",
    ):
        detector.detect(
            bars=(
                make_source_bar(),
                make_displacement_bar(),
            ),
            structure=None,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    (
        "keyword",
        "value",
        "message",
    ),
    [
        (
            "minimum_body_ratio",
            -0.01,
            "minimum_body_ratio must be between 0 and 1",
        ),
        (
            "minimum_body_ratio",
            1.01,
            "minimum_body_ratio must be between 0 and 1",
        ),
        (
            "minimum_displacement_multiple",
            0.0,
            "minimum_displacement_multiple must be positive",
        ),
        (
            "minimum_displacement_multiple",
            -1.0,
            "minimum_displacement_multiple must be positive",
        ),
        (
            "minimum_close_location",
            -0.01,
            "minimum_close_location must be between 0 and 1",
        ),
        (
            "minimum_close_location",
            1.01,
            "minimum_close_location must be between 0 and 1",
        ),
        (
            "minimum_confidence",
            -0.01,
            "minimum_confidence must be between 0 and 100",
        ),
        (
            "minimum_confidence",
            100.01,
            "minimum_confidence must be between 0 and 100",
        ),
    ],
)
def test_invalid_detector_settings_are_rejected(
    keyword: str,
    value: float,
    message: str,
) -> None:
    values = {
        "minimum_body_ratio": 0.60,
        "minimum_displacement_multiple": 1.50,
        "minimum_close_location": 0.70,
        "minimum_confidence": 60.0,
    }

    values[keyword] = value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        OrderBlockDetector(
            **values,
        )

def test_searches_backward_for_latest_valid_candidate() -> None:
    older_source = make_source_bar(
        open_price=548.00,
        high=548.10,
        low=547.50,
        close=547.80,
        timestamp=1,
    )

    older_displacement = make_displacement_bar(
        open_price=547.75,
        high=548.70,
        low=547.70,
        close=548.60,
        timestamp=2,
    )

    neutral_bar = make_bar(
        open_price=549.00,
        high=549.20,
        low=548.80,
        close=549.00,
        timestamp=3,
    )

    latest_source = make_source_bar(
        open_price=550.00,
        high=550.10,
        low=549.50,
        close=549.80,
        timestamp=4,
    )

    latest_displacement = make_displacement_bar(
        open_price=549.75,
        high=550.70,
        low=549.70,
        close=550.60,
        timestamp=5,
    )

    detector = OrderBlockDetector()

    result = detector.detect(
        bars=(
            older_source,
            older_displacement,
            neutral_bar,
            latest_source,
            latest_displacement,
        ),
        structure=make_structure(),
    )

    assert len(result) == 1
    assert result[0].source_bar_index == 3
    assert result[0].upper == latest_source.high
    assert result[0].lower == latest_source.low


def test_skips_invalid_latest_pair_and_finds_older_candidate() -> None:
    valid_source = make_source_bar(
        timestamp=1,
    )

    valid_displacement = make_displacement_bar(
        timestamp=2,
    )

    invalid_source = make_bar(
        open_price=551.00,
        high=551.20,
        low=550.80,
        close=551.10,
        timestamp=3,
    )

    invalid_displacement = make_bar(
        open_price=551.10,
        high=551.30,
        low=550.90,
        close=551.20,
        timestamp=4,
    )

    detector = OrderBlockDetector()

    result = detector.detect(
        bars=(
            valid_source,
            valid_displacement,
            invalid_source,
            invalid_displacement,
        ),
        structure=make_structure(),
    )

    assert len(result) == 1
    assert result[0].source_bar_index == 0


def test_search_lookback_limits_candidate_search() -> None:
    valid_source = make_source_bar(
        timestamp=1,
    )

    valid_displacement = make_displacement_bar(
        timestamp=2,
    )

    later_bars = (
        make_bar(
            open_price=551.00,
            high=551.20,
            low=550.80,
            close=551.00,
            timestamp=3,
        ),
        make_bar(
            open_price=551.10,
            high=551.30,
            low=550.90,
            close=551.10,
            timestamp=4,
        ),
        make_bar(
            open_price=551.20,
            high=551.40,
            low=551.00,
            close=551.20,
            timestamp=5,
        ),
    )

    detector = OrderBlockDetector(
        search_lookback=3,
    )

    result = detector.detect(
        bars=(
            valid_source,
            valid_displacement,
            *later_bars,
        ),
        structure=make_structure(),
    )

    assert result == ()


@pytest.mark.parametrize(
    "search_lookback",
    [
        0,
        1,
    ],
)
def test_rejects_invalid_search_lookback(
    search_lookback: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="search_lookback must be at least 2",
    ):
        OrderBlockDetector(
            search_lookback=search_lookback,
        )