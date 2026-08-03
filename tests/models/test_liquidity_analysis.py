from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    LiquidityAnalysis,
    LiquidityBias,
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)


def make_pool(
    *,
    side: LiquiditySide = LiquiditySide.BUY_SIDE,
    price: float = 550.00,
    importance: LiquidityImportance = LiquidityImportance.MAJOR,
    confidence: float = 94.0,
) -> LiquidityPool:
    point = LiquidityPoint(
        price=price,
        side=side,
        first_index=10,
        second_index=20,
        strength=3,
    )

    finding = LiquidityFinding(
        point=point,
        liquidity_type=(
            LiquidityType.EQUAL_HIGH
            if side is LiquiditySide.BUY_SIDE
            else LiquidityType.EQUAL_LOW
        ),
        importance=importance,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=92.0,
        state=LiquidityState.ACTIVE,
        reason="Confirmed liquidity.",
        evidence=("Liquidity confirmed.",),
        source="UnitTestDetector",
    )

    return LiquidityPool(
        price=price,
        upper=price + 0.05,
        lower=price - 0.05,
        side=side,
        importance=importance,
        confidence=confidence,
        strength=5.0,
        findings=(finding,),
        reason="Institutional liquidity pool.",
        evidence=("Institutional pool confirmed.",),
    )


def make_analysis() -> LiquidityAnalysis:
    buy_pool = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=550.00,
    )

    sell_pool = make_pool(
        side=LiquiditySide.SELL_SIDE,
        price=545.00,
        importance=LiquidityImportance.INTERMEDIATE,
        confidence=88.0,
    )

    return LiquidityAnalysis(
        institutional_bias=LiquidityBias.BUY_SIDE_DOMINANT,
        nearest_active_buy_pool=buy_pool,
        nearest_active_sell_pool=sell_pool,
        strongest_pool=buy_pool,
        active_pool_count=2,
        swept_pool_count=1,
        consumed_pool_count=0,
        confidence=91.0,
        opinion=(
            "Active buy-side liquidity remains dominant, while "
            "sell-side liquidity provides the nearest opposing target."
        ),
        evidence=(
            "Two active liquidity pools remain.",
            "One liquidity pool has already been swept.",
        ),
        warnings=(),
    )


def test_liquidity_analysis_fields() -> None:
    analysis = make_analysis()

    assert (
        analysis.institutional_bias
        is LiquidityBias.BUY_SIDE_DOMINANT
    )
    assert analysis.active_pool_count == 2
    assert analysis.swept_pool_count == 1
    assert analysis.consumed_pool_count == 0
    assert analysis.confidence == 91.0
    assert analysis.strongest_pool is not None
    assert analysis.strongest_pool.price == 550.00


def test_liquidity_analysis_is_frozen() -> None:
    analysis = make_analysis()

    with pytest.raises(FrozenInstanceError):
        analysis.confidence = 50.0  # type: ignore[misc]


def test_has_active_buy_liquidity() -> None:
    analysis = make_analysis()

    assert analysis.has_active_buy_liquidity is True


def test_has_active_sell_liquidity() -> None:
    analysis = make_analysis()

    assert analysis.has_active_sell_liquidity is True


def test_has_major_liquidity() -> None:
    analysis = make_analysis()

    assert analysis.has_major_liquidity is True


def test_total_known_pools() -> None:
    analysis = make_analysis()

    assert analysis.total_known_pools == 3


def test_no_active_buy_liquidity_helper() -> None:
    analysis = make_analysis()

    without_buy = LiquidityAnalysis(
        institutional_bias=LiquidityBias.SELL_SIDE_DOMINANT,
        nearest_active_buy_pool=None,
        nearest_active_sell_pool=analysis.nearest_active_sell_pool,
        strongest_pool=analysis.nearest_active_sell_pool,
        active_pool_count=1,
        swept_pool_count=1,
        consumed_pool_count=0,
        confidence=85.0,
        opinion="No active buy-side liquidity remains.",
        evidence=("Only sell-side liquidity remains active.",),
        warnings=(),
    )

    assert without_buy.has_active_buy_liquidity is False
    assert without_buy.has_active_sell_liquidity is True


def test_no_active_sell_liquidity_helper() -> None:
    analysis = make_analysis()

    without_sell = LiquidityAnalysis(
        institutional_bias=LiquidityBias.BUY_SIDE_DOMINANT,
        nearest_active_buy_pool=analysis.nearest_active_buy_pool,
        nearest_active_sell_pool=None,
        strongest_pool=analysis.nearest_active_buy_pool,
        active_pool_count=1,
        swept_pool_count=0,
        consumed_pool_count=1,
        confidence=87.0,
        opinion="No active sell-side liquidity remains.",
        evidence=("Only buy-side liquidity remains active.",),
        warnings=(),
    )

    assert without_sell.has_active_buy_liquidity is True
    assert without_sell.has_active_sell_liquidity is False


def test_no_strongest_pool_helper() -> None:
    analysis = LiquidityAnalysis(
        institutional_bias=LiquidityBias.UNKNOWN,
        nearest_active_buy_pool=None,
        nearest_active_sell_pool=None,
        strongest_pool=None,
        active_pool_count=0,
        swept_pool_count=0,
        consumed_pool_count=0,
        confidence=0.0,
        opinion="No institutional liquidity is currently available.",
        evidence=("No liquidity pools were available.",),
        warnings=("Liquidity analysis is incomplete.",),
    )

    assert analysis.has_major_liquidity is False
    assert analysis.total_known_pools == 0


def test_rejects_invalid_liquidity_bias() -> None:
    with pytest.raises(
        TypeError,
        match="institutional_bias must be a LiquidityBias",
    ):
        LiquidityAnalysis(
            institutional_bias="BUY_SIDE_DOMINANT",  # type: ignore[arg-type]
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=0.0,
            opinion="No liquidity.",
            evidence=("No liquidity.",),
            warnings=(),
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -1.0,
        101.0,
    ],
)
def test_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence must be between 0 and 100",
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=confidence,
            opinion="No liquidity.",
            evidence=("No liquidity.",),
            warnings=(),
        )


@pytest.mark.parametrize(
    (
        "active_pool_count",
        "swept_pool_count",
        "consumed_pool_count",
        "message",
    ),
    [
        (
            -1,
            0,
            0,
            "active_pool_count cannot be negative",
        ),
        (
            0,
            -1,
            0,
            "swept_pool_count cannot be negative",
        ),
        (
            0,
            0,
            -1,
            "consumed_pool_count cannot be negative",
        ),
    ],
)
def test_rejects_negative_pool_counts(
    active_pool_count: int,
    swept_pool_count: int,
    consumed_pool_count: int,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=active_pool_count,
            swept_pool_count=swept_pool_count,
            consumed_pool_count=consumed_pool_count,
            confidence=0.0,
            opinion="No liquidity.",
            evidence=("No liquidity.",),
            warnings=(),
        )


def test_rejects_empty_opinion() -> None:
    with pytest.raises(
        ValueError,
        match="opinion cannot be empty",
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=0.0,
            opinion="",
            evidence=("No liquidity.",),
            warnings=(),
        )


def test_rejects_whitespace_only_opinion() -> None:
    with pytest.raises(
        ValueError,
        match="opinion cannot be empty",
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=0.0,
            opinion="   ",
            evidence=("No liquidity.",),
            warnings=(),
        )


def test_rejects_empty_evidence_entry() -> None:
    with pytest.raises(
        ValueError,
        match="Evidence entries cannot be empty",
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=0.0,
            opinion="No liquidity.",
            evidence=("No liquidity.", ""),
            warnings=(),
        )


def test_rejects_empty_warning_entry() -> None:
    with pytest.raises(
        ValueError,
        match="Warning entries cannot be empty",
    ):
        LiquidityAnalysis(
            institutional_bias=LiquidityBias.UNKNOWN,
            nearest_active_buy_pool=None,
            nearest_active_sell_pool=None,
            strongest_pool=None,
            active_pool_count=0,
            swept_pool_count=0,
            consumed_pool_count=0,
            confidence=0.0,
            opinion="No liquidity.",
            evidence=("No liquidity.",),
            warnings=("",),
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "nearest_active_buy_pool",
        "nearest_active_sell_pool",
        "strongest_pool",
    ],
)
def test_rejects_invalid_optional_pool_types(
    field_name: str,
) -> None:
    values = {
        "institutional_bias": LiquidityBias.UNKNOWN,
        "nearest_active_buy_pool": None,
        "nearest_active_sell_pool": None,
        "strongest_pool": None,
        "active_pool_count": 0,
        "swept_pool_count": 0,
        "consumed_pool_count": 0,
        "confidence": 0.0,
        "opinion": "No liquidity.",
        "evidence": ("No liquidity.",),
        "warnings": (),
    }

    values[field_name] = "not-a-pool"

    with pytest.raises(
        TypeError,
        match="Optional pool fields must contain LiquidityPool objects",
    ):
        LiquidityAnalysis(
            **values,  # type: ignore[arg-type]
        )