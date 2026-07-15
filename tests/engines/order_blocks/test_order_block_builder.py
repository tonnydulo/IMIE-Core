
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.engines.order_blocks import (
    OrderBlockBuilder,
    OrderBlockCandidate,
)
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
    timestamp: int,
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


def make_source_bar() -> MarketBar:
    return make_bar(
        open_price=550.00,
        high=550.10,
        low=549.50,
        close=549.80,
        timestamp=1,
    )


def make_displacement_bar() -> MarketBar:
    return make_bar(
        open_price=549.75,
        high=550.70,
        low=549.70,
        close=550.60,
        timestamp=2,
    )


def make_candidate(
    *,
    displacement_score: float = 90.0,
    source_index: int = 10,
    displacement_index: int = 11,
    source_bar: MarketBar | None = None,
    displacement_bar: MarketBar | None = None,
) -> OrderBlockCandidate:
    return OrderBlockCandidate(
        source_index=source_index,
        displacement_index=displacement_index,
        source_bar=source_bar or make_source_bar(),
        displacement_bar=(
            displacement_bar
            or make_displacement_bar()
        ),
        displacement_score=displacement_score,
    )


def make_structure(
    *,
    bullish_break: bool = True,
    bullish_choch: bool = False,
    bullish_mss: bool = False,
) -> StructureResult:
    has_break = (
        bullish_break
        or bullish_choch
        or bullish_mss
    )

    return StructureResult(
        symbol="SPY",
        direction="long",
        state=(
            "BULLISH_MSS"
            if bullish_mss
            else "BULLISH_CHOCH"
            if bullish_choch
            else "BULLISH_STRUCTURE"
            if bullish_break
            else "NEUTRAL_STRUCTURE"
        ),
        confidence=90.0,
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
        ),
        warnings=(),
        reason="Bullish structure confirmed.",
    )


def test_builds_bullish_finding() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(),
    )

    assert isinstance(
        finding,
        OrderBlockFinding,
    )
    assert finding.side is OrderBlockSide.BULLISH


def test_uses_source_candle_range() -> None:
    builder = OrderBlockBuilder()

    source = make_bar(
        open_price=550.20,
        high=550.40,
        low=549.20,
        close=549.80,
        timestamp=1,
    )

    finding = builder.build_bullish(
        candidate=make_candidate(
            source_bar=source,
        ),
        structure=make_structure(),
    )

    assert finding.upper == 550.40
    assert finding.lower == 549.20


def test_uses_candidate_source_index() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(
            source_index=25,
        ),
        structure=make_structure(),
    )

    assert finding.source_bar_index == 25


def test_uses_candidate_strength() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(
            displacement_score=87.25,
        ),
        structure=make_structure(),
    )

    assert finding.strength == 87.25


def test_displacement_is_normalized_positive() -> None:
    builder = OrderBlockBuilder()

    source = make_bar(
        open_price=550.00,
        high=551.00,
        low=549.50,
        close=549.80,
        timestamp=1,
    )

    displacement = make_bar(
        open_price=549.70,
        high=550.50,
        low=549.60,
        close=550.40,
        timestamp=2,
    )

    finding = builder.build_bullish(
        candidate=make_candidate(
            source_bar=source,
            displacement_bar=displacement,
        ),
        structure=make_structure(),
    )

    assert finding.displacement == 0.0


def test_origin_resolves_bos() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(
            bullish_break=True,
            bullish_choch=False,
            bullish_mss=False,
        ),
    )

    assert finding.origin is OrderBlockOrigin.BOS


def test_origin_resolves_choch() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=False,
        ),
    )

    assert finding.origin is OrderBlockOrigin.CHOCH


def test_origin_resolves_mss() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=True,
        ),
    )

    assert finding.origin is OrderBlockOrigin.MSS


def test_mss_confidence_exceeds_choch_confidence() -> None:
    builder = OrderBlockBuilder()
    candidate = make_candidate(
        displacement_score=80.0,
    )

    choch = builder.build_bullish(
        candidate=candidate,
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=False,
        ),
    )

    mss = builder.build_bullish(
        candidate=candidate,
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=True,
        ),
    )

    assert mss.confidence > choch.confidence


def test_choch_confidence_exceeds_bos_confidence() -> None:
    builder = OrderBlockBuilder()
    candidate = make_candidate(
        displacement_score=80.0,
    )

    bos = builder.build_bullish(
        candidate=candidate,
        structure=make_structure(
            bullish_break=True,
            bullish_choch=False,
            bullish_mss=False,
        ),
    )

    choch = builder.build_bullish(
        candidate=candidate,
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=False,
        ),
    )

    assert choch.confidence > bos.confidence


def test_confidence_is_capped_at_one_hundred() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(
            displacement_score=100.0,
        ),
        structure=make_structure(
            bullish_break=True,
            bullish_choch=True,
            bullish_mss=True,
        ),
    )

    assert finding.confidence == 100.0


def test_reason_is_populated() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(),
    )

    assert finding.reason.strip()


def test_evidence_is_populated() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(),
    )

    assert finding.evidence
    assert all(
        item.strip()
        for item in finding.evidence
    )


def test_evidence_mentions_source_index() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(
            source_index=18,
        ),
        structure=make_structure(),
    )

    assert any(
        "18" in item
        for item in finding.evidence
    )


def test_detector_metadata_is_populated() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(),
    )

    assert finding.detector == "OrderBlockBuilder"


def test_finding_is_frozen() -> None:
    builder = OrderBlockBuilder()

    finding = builder.build_bullish(
        candidate=make_candidate(),
        structure=make_structure(),
    )

    with pytest.raises(FrozenInstanceError):
        finding.confidence = 50.0  # type: ignore[misc]


def test_rejects_invalid_candidate_type() -> None:
    builder = OrderBlockBuilder()

    with pytest.raises(
        TypeError,
        match="candidate must be an OrderBlockCandidate",
    ):
        builder.build_bullish(
            candidate=None,  # type: ignore[arg-type]
            structure=make_structure(),
        )


def test_rejects_invalid_structure_type() -> None:
    builder = OrderBlockBuilder()

    with pytest.raises(
        TypeError,
        match="structure must be a StructureResult",
    ):
        builder.build_bullish(
            candidate=make_candidate(),
            structure=None,  # type: ignore[arg-type]
        )


def test_rejects_missing_bullish_confirmation() -> None:
    builder = OrderBlockBuilder()

    with pytest.raises(
        ValueError,
        match="bullish structure confirmation",
    ):
        builder.build_bullish(
            candidate=make_candidate(),
            structure=make_structure(
                bullish_break=False,
                bullish_choch=False,
                bullish_mss=False,
            ),
        )