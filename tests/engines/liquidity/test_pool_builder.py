import pytest

from imie.engines.liquidity import LiquidityPoolBuilder
from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)


def make_finding(
    *,
    price: float,
    side: LiquiditySide,
    first_index: int,
    second_index: int,
    confidence: float = 80.0,
    strength: int = 2,
    importance: LiquidityImportance = LiquidityImportance.MINOR,
    state: LiquidityState = LiquidityState.ACTIVE,
    source: str = "TestDetector",
) -> LiquidityFinding:
    liquidity_type = (
        LiquidityType.EQUAL_HIGH
        if side is LiquiditySide.BUY_SIDE
        else LiquidityType.EQUAL_LOW
    )

    point = LiquidityPoint(
        price=price,
        side=side,
        first_index=first_index,
        second_index=second_index,
        strength=strength,
    )

    return LiquidityFinding(
        point=point,
        liquidity_type=liquidity_type,
        importance=importance,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=confidence,
        state=state,
        reason=f"Liquidity detected at {price:.2f}.",
        evidence=(
            f"Confirmed liquidity at {price:.2f}.",
        ),
        source=source,
    )


def test_builds_single_finding_pool() -> None:
    builder = LiquidityPoolBuilder()

    finding = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    pools = builder.build((finding,))

    assert len(pools) == 1

    pool = pools[0]

    assert pool.price == pytest.approx(550.00)
    assert pool.lower == pytest.approx(550.00)
    assert pool.upper == pytest.approx(550.00)
    assert pool.side is LiquiditySide.BUY_SIDE
    assert pool.finding_count == 1
    assert pool.findings == (finding,)


def test_merges_nearby_findings_on_same_side() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    first = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    second = make_finding(
        price=550.06,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
    )

    pools = builder.build(
        (
            first,
            second,
        )
    )

    assert len(pools) == 1

    pool = pools[0]

    assert pool.finding_count == 2
    assert pool.lower == pytest.approx(550.00)
    assert pool.upper == pytest.approx(550.06)
    assert pool.strength == pytest.approx(4.0)


def test_does_not_merge_opposite_sides() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=1.00,
    )

    buy_side = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    sell_side = make_finding(
        price=550.02,
        side=LiquiditySide.SELL_SIDE,
        first_index=20,
        second_index=24,
    )

    pools = builder.build(
        (
            buy_side,
            sell_side,
        )
    )

    assert len(pools) == 2
    assert {
        pool.side
        for pool in pools
    } == {
        LiquiditySide.BUY_SIDE,
        LiquiditySide.SELL_SIDE,
    }


def test_does_not_merge_findings_outside_tolerance() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    first = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    second = make_finding(
        price=550.11,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
    )

    pools = builder.build(
        (
            first,
            second,
        )
    )

    assert len(pools) == 2


def test_complete_span_prevents_chain_clustering() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    findings = (
        make_finding(
            price=550.00,
            side=LiquiditySide.BUY_SIDE,
            first_index=10,
            second_index=14,
        ),
        make_finding(
            price=550.08,
            side=LiquiditySide.BUY_SIDE,
            first_index=20,
            second_index=24,
        ),
        make_finding(
            price=550.16,
            side=LiquiditySide.BUY_SIDE,
            first_index=30,
            second_index=34,
        ),
    )

    pools = builder.build(findings)

    assert len(pools) == 2

    assert pools[0].finding_count == 2
    assert pools[0].lower == pytest.approx(550.00)
    assert pools[0].upper == pytest.approx(550.08)

    assert pools[1].finding_count == 1
    assert pools[1].price == pytest.approx(550.16)


def test_findings_are_sorted_before_clustering() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    high = make_finding(
        price=550.08,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
    )

    low = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    pools = builder.build(
        (
            high,
            low,
        )
    )

    assert len(pools) == 1
    assert pools[0].lower == pytest.approx(550.00)
    assert pools[0].upper == pytest.approx(550.08)


def test_pool_price_is_confidence_and_strength_weighted() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=1.00,
        confluence_bonus=0.0,
    )

    weaker = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        confidence=50.0,
        strength=1,
    )

    stronger = make_finding(
        price=551.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
        confidence=100.0,
        strength=3,
    )

    pools = builder.build(
        (
            weaker,
            stronger,
        )
    )

    expected = (
        550.00 * 50.0 * 1
        + 551.00 * 100.0 * 3
    ) / (
        50.0 * 1
        + 100.0 * 3
    )

    assert pools[0].price == pytest.approx(
        expected,
        abs=0.000001,
    )


def test_pool_uses_highest_importance() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    minor = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        importance=LiquidityImportance.MINOR,
    )

    major = make_finding(
        price=550.05,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
        importance=LiquidityImportance.MAJOR,
    )

    pools = builder.build(
        (
            minor,
            major,
        )
    )

    assert pools[0].importance is LiquidityImportance.MAJOR


def test_confluence_increases_pool_confidence() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
        confluence_bonus=3.0,
    )

    first = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        confidence=80.0,
    )

    second = make_finding(
        price=550.05,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
        confidence=80.0,
    )

    pool = builder.build(
        (
            first,
            second,
        )
    )[0]

    assert pool.confidence == pytest.approx(83.0)


def test_pool_confidence_is_capped_at_100() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
        confluence_bonus=10.0,
    )

    findings = (
        make_finding(
            price=550.00,
            side=LiquiditySide.BUY_SIDE,
            first_index=10,
            second_index=14,
            confidence=98.0,
        ),
        make_finding(
            price=550.02,
            side=LiquiditySide.BUY_SIDE,
            first_index=20,
            second_index=24,
            confidence=98.0,
        ),
    )

    pool = builder.build(findings)[0]

    assert pool.confidence == 100.0


def test_inactive_findings_are_ignored() -> None:
    builder = LiquidityPoolBuilder()

    active = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    swept = make_finding(
        price=550.05,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
        state=LiquidityState.SWEPT,
    )

    pools = builder.build(
        (
            active,
            swept,
        )
    )

    assert len(pools) == 1
    assert pools[0].findings == (active,)


def test_returns_empty_when_no_active_findings_exist() -> None:
    builder = LiquidityPoolBuilder()

    swept = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        state=LiquidityState.SWEPT,
    )

    assert builder.build((swept,)) == ()


def test_exact_duplicate_findings_are_removed() -> None:
    builder = LiquidityPoolBuilder()

    finding = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    pools = builder.build(
        (
            finding,
            finding,
        )
    )

    assert len(pools) == 1
    assert pools[0].finding_count == 1


def test_minimum_findings_filters_singleton_clusters() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
        min_findings=2,
    )

    first = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
    )

    second = make_finding(
        price=551.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
    )

    assert builder.build(
        (
            first,
            second,
        )
    ) == ()


def test_evidence_is_deduplicated() -> None:
    builder = LiquidityPoolBuilder(
        cluster_tolerance=0.10,
    )

    first = make_finding(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        source="EqualHighDetector",
    )

    second = make_finding(
        price=550.05,
        side=LiquiditySide.BUY_SIDE,
        first_index=20,
        second_index=24,
        source="EqualHighDetector",
    )

    pool = builder.build(
        (
            first,
            second,
        )
    )[0]

    assert len(pool.evidence) == len(
        set(pool.evidence)
    )


def test_rejects_non_finding_input() -> None:
    builder = LiquidityPoolBuilder()

    with pytest.raises(
        TypeError,
        match="requires LiquidityFinding",
    ):
        builder.build(
            (
                "not-a-finding",  # type: ignore[arg-type]
            )
        )


def test_rejects_negative_cluster_tolerance() -> None:
    with pytest.raises(
        ValueError,
        match="cluster_tolerance cannot be negative",
    ):
        LiquidityPoolBuilder(
            cluster_tolerance=-0.01,
        )


def test_rejects_invalid_minimum_findings() -> None:
    with pytest.raises(
        ValueError,
        match="min_findings must be at least 1",
    ):
        LiquidityPoolBuilder(
            min_findings=0,
        )


def test_rejects_negative_confluence_bonus() -> None:
    with pytest.raises(
        ValueError,
        match="confluence_bonus cannot be negative",
    ):
        LiquidityPoolBuilder(
            confluence_bonus=-1.0,
        )