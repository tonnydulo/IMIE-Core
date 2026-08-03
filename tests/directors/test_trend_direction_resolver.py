from __future__ import annotations

from dataclasses import dataclass

import pytest

from imie.directors.trend_direction_resolver import (
    TrendDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class StubTrendPayload:
    direction: object | None = None
    trend: object | None = None
    trend_direction: object | None = None
    bias: object | None = None
    market_direction: object | None = None
    state: object | None = None
    trend_state: object | None = None
    opinion: object | None = None
    reason: object | None = None
    narrative: object | None = None


def make_result(
    *,
    opinion: str = "Trend context unavailable.",
    payload: object | None = None,
    enabled: bool = True,
    confidence: float = 85.0,
) -> AnalystResult:
    return AnalystResult(
        analyst="TrendAnalyst",
        analyst_id="TREND",
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
    resolver = TrendDirectionResolver()

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
        opinion="Bullish",
        enabled=False,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_rejects_invalid_result_type() -> None:
    resolver = TrendDirectionResolver()

    with pytest.raises(
        TypeError,
        match=(
            "result must be an AnalystResult or None"
        ),
    ):
        resolver.resolve(
            object()  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [
        "long",
        "LONG",
        "bullish",
        "BULLISH",
        "up",
        "upward",
    ],
)
def test_payload_direction_resolves_bullish(
    value: str,
) -> None:
    payload = StubTrendPayload(
        direction=value,
    )

    result = make_result(
        opinion="Bearish",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "value",
    [
        "short",
        "SHORT",
        "bearish",
        "BEARISH",
        "down",
        "downward",
    ],
)
def test_payload_direction_resolves_bearish(
    value: str,
) -> None:
    payload = StubTrendPayload(
        direction=value,
    )

    result = make_result(
        opinion="Bullish",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "attribute",
    [
        "trend",
        "trend_direction",
        "bias",
        "market_direction",
    ],
)
def test_alternate_payload_direction_fields(
    attribute: str,
) -> None:
    payload = StubTrendPayload(
        **{
            attribute: "bullish",
        }
    )

    result = make_result(
        opinion="Unknown trend.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "attribute",
    [
        "state",
        "trend_state",
        "opinion",
        "reason",
        "narrative",
    ],
)
def test_payload_text_fields_resolve_bullish(
    attribute: str,
) -> None:
    payload = StubTrendPayload(
        **{
            attribute: (
                "Price is trending higher."
            ),
        }
    )

    result = make_result(
        opinion="Unknown trend.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "attribute",
    [
        "state",
        "trend_state",
        "opinion",
        "reason",
        "narrative",
    ],
)
def test_payload_text_fields_resolve_bearish(
    attribute: str,
) -> None:
    payload = StubTrendPayload(
        **{
            attribute: (
                "Price is trending lower."
            ),
        }
    )

    result = make_result(
        opinion="Unknown trend.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_payload_has_priority_over_opinion() -> None:
    payload = StubTrendPayload(
        direction="long",
    )

    result = make_result(
        opinion="Bearish trend confirmed.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_unresolved_payload_falls_back_to_opinion() -> None:
    payload = StubTrendPayload(
        direction="unknown",
        state="unresolved",
    )

    result = make_result(
        opinion="Bullish trend confirmed.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_arbitrary_payload_falls_back_to_opinion() -> None:
    result = make_result(
        opinion="Bearish trend confirmed.",
        payload=object(),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Bullish trend confirmed.",
        "Market is in an uptrend.",
        "Market is in an up trend.",
        "Price is trending higher.",
        "Buyers control the trend.",
        "Buyers are in control.",
        "Buyer control remains intact.",
        "Higher highs are forming.",
        "Higher lows are forming.",
        "Higher high confirmed.",
        "Higher low confirmed.",
        "Price remains above EMA9.",
        "Price remains above EMA 9.",
        "Price remains above VWAP.",
        "EMA9 rising.",
        "EMA 9 rising.",
        "Rising EMA9 confirms momentum.",
        "Rising EMA 9 confirms momentum.",
        "Upside momentum remains active.",
        "Positive trend remains active.",
        "Long bias confirmed.",
        "Upward trend remains active.",
        "Upward direction remains active.",
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
        "Bearish trend confirmed.",
        "Market is in a downtrend.",
        "Market is in a down trend.",
        "Price is trending lower.",
        "Sellers control the trend.",
        "Sellers are in control.",
        "Seller control remains intact.",
        "Lower highs are forming.",
        "Lower lows are forming.",
        "Lower high confirmed.",
        "Lower low confirmed.",
        "Price remains below EMA9.",
        "Price remains below EMA 9.",
        "Price remains below VWAP.",
        "EMA9 falling.",
        "EMA 9 falling.",
        "Falling EMA9 confirms momentum.",
        "Falling EMA 9 confirms momentum.",
        "Downside momentum remains active.",
        "Negative trend remains active.",
        "Short bias confirmed.",
        "Downward trend remains active.",
        "Downward direction remains active.",
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
        "Neutral trend.",
        "Trend remains balanced.",
        "Market balance remains intact.",
        "Price remains sideways.",
        "Range-bound trend.",
        "Range bound trend.",
        "Market is choppy.",
        "No trend is present.",
        "No directional trend.",
        "Mixed trend.",
        "Flat trend.",
        "EMA9 flat.",
        "EMA 9 flat.",
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
        "Unknown trend.",
        "Trend context unavailable.",
        "Trend remains unresolved.",
        "Trend is unclear.",
        "Trend is indeterminate.",
        "Waiting for trend.",
        "Insufficient trend data.",
        "No trend data.",
        "Trend not evaluated.",
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
        "bullish trend confirmed",
        "Bullish Trend Confirmed",
        "BULLISH TREND CONFIRMED",
        "  bullish   trend   confirmed  ",
        "BULLISH_TREND_CONFIRMED",
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
        "bearish trend confirmed",
        "Bearish Trend Confirmed",
        "BEARISH TREND CONFIRMED",
        "  bearish   trend   confirmed  ",
        "BEARISH_TREND_CONFIRMED",
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


def test_explicit_bullish_beats_generic_bearish_phrase() -> None:
    result = make_result(
        opinion=(
            "Bullish trend remains active despite downside "
            "momentum risk."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_explicit_bearish_beats_generic_bullish_phrase() -> None:
    result = make_result(
        opinion=(
            "Bearish trend remains active despite upside "
            "momentum risk."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_explicit_bullish_and_bearish_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Bullish trend conflicts with bearish trend."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_generic_bullish_and_bearish_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Higher highs conflict with lower lows."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_confidence_does_not_change_direction() -> None:
    result = make_result(
        opinion="Bullish trend confirmed.",
        confidence=0.0,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_evidence_does_not_override_opinion() -> None:
    result = AnalystResult(
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion="Bearish trend confirmed.",
        confidence=85.0,
        evidence=[
            "Bullish trend was previously observed.",
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
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion="Bullish trend confirmed.",
        confidence=85.0,
        evidence=[],
        warnings=[
            "Bearish reversal remains possible.",
        ],
        payload=None,
        enabled=True,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_resolver_is_frozen() -> None:
    resolver = TrendDirectionResolver()

    with pytest.raises(
        AttributeError
    ):
        resolver.new_value = True  # type: ignore[attr-defined]