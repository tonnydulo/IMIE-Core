from __future__ import annotations

from dataclasses import dataclass

import pytest

from imie.directors.liquidity_direction_resolver import (
    LiquidityDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    LiquiditySide,
)


@dataclass(frozen=True, slots=True)
class StubPool:
    side: object


@dataclass(frozen=True, slots=True)
class StubLiquidityPayload:
    institutional_bias: object | None = None
    nearest_active_buy_pool: object | None = None
    nearest_active_sell_pool: object | None = None
    nearest_buy_pool: object | None = None
    nearest_sell_pool: object | None = None
    strongest_pool: object | None = None
    direction: object | None = None


def make_result(
    *,
    opinion: str = "Liquidity context unavailable.",
    payload: object | None = None,
    enabled: bool = True,
    confidence: float = 85.0,
) -> AnalystResult:
    return AnalystResult(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=opinion,
        confidence=confidence,
        evidence=[],
        warnings=[],
        payload=payload,
        enabled=enabled,
    )


def resolve(
    result: AnalystResult | None,
) -> InstitutionalDirection:
    resolver = LiquidityDirectionResolver()

    return resolver.resolve(
        result
    )


def test_missing_result_resolves_unknown() -> None:
    assert (
        resolve(None)
        is InstitutionalDirection.UNKNOWN
    )


def test_disabled_result_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        enabled=False,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_rejects_invalid_result_type() -> None:
    resolver = LiquidityDirectionResolver()

    with pytest.raises(
        TypeError,
        match=(
            "result must be an AnalystResult or None"
        ),
    ):
        resolver.resolve(
            object()  # type: ignore[arg-type]
        )


def test_active_buy_pool_resolves_bullish() -> None:
    payload = StubLiquidityPayload(
        nearest_active_buy_pool=StubPool(
            side=LiquiditySide.BUY_SIDE,
        ),
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_active_sell_pool_resolves_bearish() -> None:
    payload = StubLiquidityPayload(
        nearest_active_sell_pool=StubPool(
            side=LiquiditySide.SELL_SIDE,
        ),
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_buy_and_sell_pools_resolve_neutral() -> None:
    payload = StubLiquidityPayload(
        nearest_active_buy_pool=StubPool(
            side=LiquiditySide.BUY_SIDE,
        ),
        nearest_active_sell_pool=StubPool(
            side=LiquiditySide.SELL_SIDE,
        ),
    )

    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.NEUTRAL
    )


def test_legacy_nearest_buy_pool_resolves_bullish() -> None:
    payload = StubLiquidityPayload(
        nearest_buy_pool=StubPool(
            side=LiquiditySide.BUY_SIDE,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_legacy_nearest_sell_pool_resolves_bearish() -> None:
    payload = StubLiquidityPayload(
        nearest_sell_pool=StubPool(
            side=LiquiditySide.SELL_SIDE,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_strongest_buy_side_pool_resolves_bullish() -> None:
    payload = StubLiquidityPayload(
        strongest_pool=StubPool(
            side=LiquiditySide.BUY_SIDE,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_strongest_sell_side_pool_resolves_bearish() -> None:
    payload = StubLiquidityPayload(
        strongest_pool=StubPool(
            side=LiquiditySide.SELL_SIDE,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "side",
    [
        "BUY_SIDE",
        "BUY SIDE",
        "BUYSIDE",
        "BUY",
    ],
)
def test_string_buy_pool_side_resolves_bullish(
    side: str,
) -> None:
    payload = StubLiquidityPayload(
        strongest_pool=StubPool(
            side=side,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "side",
    [
        "SELL_SIDE",
        "SELL SIDE",
        "SELLSIDE",
        "SELL",
    ],
)
def test_string_sell_pool_side_resolves_bearish(
    side: str,
) -> None:
    payload = StubLiquidityPayload(
        strongest_pool=StubPool(
            side=side,
        ),
    )

    result = make_result(
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_unknown_pool_side_falls_back_to_opinion() -> None:
    payload = StubLiquidityPayload(
        strongest_pool=StubPool(
            side="UNRESOLVED",
        ),
    )

    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_bullish_institutional_bias_resolves_bullish() -> None:
    payload = StubLiquidityPayload(
        institutional_bias="BULLISH",
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_bearish_institutional_bias_resolves_bearish() -> None:
    payload = StubLiquidityPayload(
        institutional_bias="BEARISH",
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_balanced_institutional_bias_resolves_neutral() -> None:
    payload = StubLiquidityPayload(
        institutional_bias="BALANCED",
    )

    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.NEUTRAL
    )


def test_long_payload_direction_resolves_bullish() -> None:
    payload = StubLiquidityPayload(
        direction="long",
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_short_payload_direction_resolves_bearish() -> None:
    payload = StubLiquidityPayload(
        direction="short",
    )

    result = make_result(
        opinion="Unknown liquidity.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_payload_has_priority_over_opinion() -> None:
    payload = StubLiquidityPayload(
        nearest_active_buy_pool=StubPool(
            side=LiquiditySide.BUY_SIDE,
        ),
    )

    result = make_result(
        opinion=(
            "Institutional liquidity supply remains active."
        ),
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_non_directional_payload_falls_back_to_opinion() -> None:
    payload = StubLiquidityPayload(
        institutional_bias="UNKNOWN",
        direction="neutral",
    )

    result = make_result(
        opinion=(
            "Institutional liquidity supply remains active."
        ),
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_arbitrary_payload_falls_back_to_opinion() -> None:
    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        payload=object(),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional liquidity demand remains active.",
        "Demand liquidity remains below price.",
        "Institutional support liquidity remains active.",
        "Buy-side liquidity remains active.",
        "Buy side liquidity remains active.",
        "Buyside liquidity remains active.",
        "Buy liquidity remains active.",
        "Buyers continue to defend liquidity.",
        "Liquidity remains below price.",
        "Sell-side liquidity swept.",
        "Sell side liquidity swept.",
        "Sellside liquidity swept.",
        "Sell-side sweep confirmed.",
        "Downside liquidity swept.",
    ],
)
def test_bullish_opinions_resolve_bullish(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional liquidity supply remains active.",
        "Supply liquidity remains above price.",
        "Institutional resistance liquidity remains active.",
        "Sell-side liquidity remains active.",
        "Sell side liquidity remains active.",
        "Sellside liquidity remains active.",
        "Sell liquidity remains active.",
        "Sellers continue to defend liquidity.",
        "Liquidity remains above price.",
        "Buy-side liquidity swept.",
        "Buy side liquidity swept.",
        "Buyside liquidity swept.",
        "Buy-side sweep confirmed.",
        "Upside liquidity swept.",
    ],
)
def test_bearish_opinions_resolve_bearish(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional liquidity remains neutral.",
        "Institutional liquidity remains balanced.",
        "Liquidity balance is present.",
        "Liquidity remains active on both sides.",
        "Both sides active.",
        "Liquidity on both sides.",
        "Two-sided liquidity remains active.",
        "Two sided liquidity remains active.",
    ],
)
def test_neutral_opinions_resolve_neutral(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Unknown liquidity.",
        "Liquidity context unavailable.",
        "Liquidity remains unresolved.",
        "Liquidity is unclear.",
        "Liquidity is indeterminate.",
        "No actionable liquidity.",
        "No active liquidity.",
        "No liquidity is available.",
        "Waiting for liquidity.",
        "Observation complete.",
    ],
)
def test_unknown_opinions_resolve_unknown(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "institutional liquidity demand remains active",
        "Institutional Liquidity Demand Remains Active",
        "INSTITUTIONAL LIQUIDITY DEMAND REMAINS ACTIVE",
        "  institutional   liquidity   demand   remains active ",
        "INSTITUTIONAL_LIQUIDITY_DEMAND_REMAINS_ACTIVE",
    ],
)
def test_bullish_resolution_is_case_and_spacing_insensitive(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "institutional liquidity supply remains active",
        "Institutional Liquidity Supply Remains Active",
        "INSTITUTIONAL LIQUIDITY SUPPLY REMAINS ACTIVE",
        "  institutional   liquidity   supply   remains active ",
        "INSTITUTIONAL_LIQUIDITY_SUPPLY_REMAINS_ACTIVE",
    ],
)
def test_bearish_resolution_is_case_and_spacing_insensitive(
    opinion: str,
) -> None:
    result = make_result(
        opinion=opinion,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_ambiguous_demand_and_supply_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Institutional demand and institutional supply "
            "are both active."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_ambiguous_buy_and_sell_side_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Buy-side and sell-side liquidity are both active."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_confidence_does_not_change_direction() -> None:
    result = make_result(
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        confidence=0.0,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_evidence_does_not_override_opinion() -> None:
    result = AnalystResult(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=(
            "Institutional liquidity supply remains active."
        ),
        confidence=85.0,
        evidence=[
            "Demand liquidity was previously observed.",
        ],
        warnings=[],
        payload=None,
        enabled=True,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_warnings_do_not_override_opinion() -> None:
    result = AnalystResult(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        confidence=85.0,
        evidence=[],
        warnings=[
            "Supply liquidity may form later.",
        ],
        payload=None,
        enabled=True,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_resolver_is_frozen() -> None:
    resolver = LiquidityDirectionResolver()

    with pytest.raises(
        AttributeError
    ):
        resolver.new_value = True  # type: ignore[attr-defined]