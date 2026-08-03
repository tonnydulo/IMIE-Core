from __future__ import annotations

import pytest

from imie.directors.structure_direction_resolver import (
    StructureDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    StructureResult,
)


def make_structure_result(
    *,
    direction: str = "neutral",
    state: str = "NEUTRAL_STRUCTURE",
    bullish_break: bool = False,
    bearish_break: bool = False,
    bullish_break_level: float | None = None,
    bearish_break_level: float | None = None,
    break_confirmation_price: float | None = None,
    bullish_choch: bool = False,
    bearish_choch: bool = False,
    bullish_mss: bool = False,
    bearish_mss: bool = False,
    reason: str = "",
) -> StructureResult:
    return StructureResult(
        symbol="SPY",
        direction=direction,
        state=state,
        confidence=85.0,
        nearest_support=500.0,
        nearest_resistance=510.0,
        structural_target=None,
        structural_stop=None,
        projected_reward=None,
        projected_risk=None,
        projected_rr=None,
        swing_high_count=2,
        swing_low_count=2,
        bullish_break=bullish_break,
        bearish_break=bearish_break,
        bullish_break_level=bullish_break_level,
        bearish_break_level=bearish_break_level,
        break_confirmation_price=(
            break_confirmation_price
        ),
        bullish_choch=bullish_choch,
        bearish_choch=bearish_choch,
        bullish_mss=bullish_mss,
        bearish_mss=bearish_mss,
        mss_confidence=(
            90.0
            if bullish_mss or bearish_mss
            else 0.0
        ),
        mss_reason=reason,
        evidence=(),
        warnings=(),
        reason=reason,
    )


def make_result(
    *,
    opinion: str = "Structure unavailable.",
    payload: object | None = None,
    enabled: bool = True,
) -> AnalystResult:
    return AnalystResult(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion=opinion,
        confidence=85.0,
        evidence=[],
        warnings=[],
        payload=payload,
        enabled=enabled,
    )


def resolve(
    result: AnalystResult | None,
) -> InstitutionalDirection:
    resolver = StructureDirectionResolver()

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
        opinion="Bullish structure confirmed.",
        enabled=False,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_rejects_invalid_result_type() -> None:
    resolver = StructureDirectionResolver()

    with pytest.raises(
        TypeError,
        match=(
            "result must be an AnalystResult or None"
        ),
    ):
        resolver.resolve(
            object()  # type: ignore[arg-type]
        )


def test_bullish_break_payload_resolves_bullish() -> None:
    payload = make_structure_result(
        direction="long",
        state="BULLISH_STRUCTURE",
        bullish_break=True,
        bullish_break_level=505.0,
        break_confirmation_price=506.0,
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_bearish_break_payload_resolves_bearish() -> None:
    payload = make_structure_result(
        direction="short",
        state="BEARISH_STRUCTURE",
        bearish_break=True,
        bearish_break_level=500.0,
        break_confirmation_price=499.0,
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_bullish_choch_payload_resolves_bullish() -> None:
    payload = make_structure_result(
        direction="long",
        state="BULLISH_TRANSITION",
        bullish_break=True,
        bullish_break_level=505.0,
        break_confirmation_price=506.0,
        bullish_choch=True,
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_bearish_choch_payload_resolves_bearish() -> None:
    payload = make_structure_result(
        direction="short",
        state="BEARISH_TRANSITION",
        bearish_break=True,
        bearish_break_level=500.0,
        break_confirmation_price=499.0,
        bearish_choch=True,
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_bullish_mss_payload_resolves_bullish() -> None:
    payload = make_structure_result(
        direction="long",
        state="BULLISH_SHIFT",
        bullish_break=True,
        bullish_break_level=505.0,
        break_confirmation_price=506.0,
        bullish_choch=True,
        bullish_mss=True,
        reason=(
            "Bullish Market Structure Shift confirms "
            "institutional control."
        ),
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_bearish_mss_payload_resolves_bearish() -> None:
    payload = make_structure_result(
        direction="short",
        state="BEARISH_SHIFT",
        bearish_break=True,
        bearish_break_level=500.0,
        break_confirmation_price=499.0,
        bearish_choch=True,
        bearish_mss=True,
        reason=(
            "Bearish Market Structure Shift confirms "
            "institutional control."
        ),
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_long_payload_direction_resolves_bullish() -> None:
    payload = make_structure_result(
        direction="long",
        state="STRUCTURE_DEVELOPING",
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_short_payload_direction_resolves_bearish() -> None:
    payload = make_structure_result(
        direction="short",
        state="STRUCTURE_DEVELOPING",
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_neutral_payload_falls_back_to_state() -> None:
    payload = make_structure_result(
        direction="neutral",
        state="BULLISH_STRUCTURE",
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_neutral_payload_state_resolves_neutral() -> None:
    payload = make_structure_result(
        direction="neutral",
        state="BALANCED_STRUCTURE",
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.NEUTRAL
    )


def test_payload_reason_can_resolve_bullish() -> None:
    payload = make_structure_result(
        direction="neutral",
        state="UNRESOLVED",
        reason=(
            "Institutional control shifted to buyers."
        ),
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_payload_reason_can_resolve_bearish() -> None:
    payload = make_structure_result(
        direction="neutral",
        state="UNRESOLVED",
        reason=(
            "Institutional control shifted to sellers."
        ),
    )

    result = make_result(
        opinion="Unknown.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_payload_has_priority_over_opinion() -> None:
    payload = make_structure_result(
        direction="long",
        state="BULLISH_STRUCTURE",
    )

    result = make_result(
        opinion="Bearish structure confirmed.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_unresolved_payload_falls_back_to_opinion() -> None:
    payload = make_structure_result(
        direction="neutral",
        state="UNRESOLVED",
        reason="",
    )

    result = make_result(
        opinion="Bearish structure confirmed.",
        payload=payload,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BEARISH
    )


def test_non_structure_payload_falls_back_to_opinion() -> None:
    result = make_result(
        opinion="Bullish structure confirmed.",
        payload=object(),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Bullish structure confirmed.",
        "Buyers control market structure.",
        "Buyers are in control.",
        "Upside structure remains intact.",
        "Upward structure remains intact.",
        "Higher high confirmed.",
        "Higher low confirmed.",
        "Bullish BOS confirmed.",
        "Bullish Break of Structure confirmed.",
        "Bullish CHOCH confirmed.",
        "Bullish Change of Character confirmed.",
        "Bullish MSS confirmed.",
        "Bullish Market Structure Shift confirmed.",
        "Control shifted to buyers.",
        (
            "Institutional control transitioned from "
            "sellers to buyers."
        ),
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
        "Bearish structure confirmed.",
        "Sellers control market structure.",
        "Sellers are in control.",
        "Downside structure remains intact.",
        "Downward structure remains intact.",
        "Lower high confirmed.",
        "Lower low confirmed.",
        "Bearish BOS confirmed.",
        "Bearish Break of Structure confirmed.",
        "Bearish CHOCH confirmed.",
        "Bearish Change of Character confirmed.",
        "Bearish MSS confirmed.",
        "Bearish Market Structure Shift confirmed.",
        "Control shifted to sellers.",
        (
            "Institutional control transitioned from "
            "buyers to sellers."
        ),
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
        "Neutral structure.",
        "Balanced structure.",
        "Market structure is balanced.",
        "Range-bound structure.",
        "Range bound structure.",
        "Sideways structure.",
        "No directional structure.",
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
        "Unknown.",
        "Structure unavailable.",
        "Structure unresolved.",
        "Structure is unclear.",
        "Structure is indeterminate.",
        "Waiting for structure.",
        "No structure available.",
        "No structural confirmation.",
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
        "bullish structure confirmed",
        "Bullish Structure Confirmed",
        "BULLISH STRUCTURE CONFIRMED",
        "  bullish   structure   confirmed  ",
        "BULLISH_STRUCTURE_CONFIRMED",
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
        "bearish structure confirmed",
        "Bearish Structure Confirmed",
        "BEARISH STRUCTURE CONFIRMED",
        "  bearish   structure   confirmed  ",
        "BEARISH_STRUCTURE_CONFIRMED",
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


def test_ambiguous_opinion_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Bullish structure conflicts with bearish structure."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_ambiguous_bos_opinion_resolves_unknown() -> None:
    result = make_result(
        opinion=(
            "Bullish BOS and bearish BOS are both reported."
        ),
    )

    assert (
        resolve(result)
        is InstitutionalDirection.UNKNOWN
    )


def test_confidence_does_not_change_direction() -> None:
    result = AnalystResult(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion="Bullish structure confirmed.",
        confidence=0.0,
        evidence=[],
        warnings=[],
        payload=None,
        enabled=True,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_evidence_does_not_override_opinion() -> None:
    result = AnalystResult(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion="Bearish structure confirmed.",
        confidence=85.0,
        evidence=[
            "Bullish structure mentioned elsewhere.",
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
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion="Bullish structure confirmed.",
        confidence=85.0,
        evidence=[],
        warnings=[
            "Bearish risk remains possible.",
        ],
        payload=None,
        enabled=True,
    )

    assert (
        resolve(result)
        is InstitutionalDirection.BULLISH
    )


def test_resolver_is_frozen() -> None:
    resolver = StructureDirectionResolver()

    with pytest.raises(
        AttributeError
    ):
        resolver.new_value = True  # type: ignore[attr-defined]