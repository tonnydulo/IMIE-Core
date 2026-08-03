from __future__ import annotations

from dataclasses import dataclass

import pytest

from imie.directors.extended_bias_direction_resolver import (
    ExtendedBiasDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class StubPayload:
    direction: object | None = None
    bias: object | None = None
    institutional_direction: object | None = None
    market_direction: object | None = None
    control_direction: object | None = None
    pressure_direction: object | None = None
    participation_direction: object | None = None
    value_direction: object | None = None
    state: object | None = None
    control: object | None = None
    acceptance: object | None = None
    pressure: object | None = None
    participation: object | None = None
    value_state: object | None = None
    opinion: object | None = None
    reason: object | None = None
    narrative: object | None = None


def make_result(
    *,
    domain: str,
    opinion: str,
    payload: object | None = None,
    enabled: bool = True,
    confidence: float = 80.0,
) -> AnalystResult:
    return AnalystResult(
        analyst=f"{domain.title()}Analyst",
        analyst_id=domain,
        opinion=opinion,
        confidence=confidence,
        evidence=[],
        warnings=[],
        payload=payload,
        enabled=enabled,
    )


def resolve(
    *,
    domain: str,
    opinion: str,
    payload: object | None = None,
    enabled: bool = True,
) -> InstitutionalDirection:
    resolver = ExtendedBiasDirectionResolver()

    return resolver.resolve(
        domain=domain,
        result=make_result(
            domain=domain,
            opinion=opinion,
            payload=payload,
            enabled=enabled,
        ),
    )


@pytest.mark.parametrize(
    "domain",
    [
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
def test_missing_result_resolves_unknown(
    domain: str,
) -> None:
    resolver = ExtendedBiasDirectionResolver()

    assert (
        resolver.resolve(
            domain=domain,
            result=None,
        )
        is InstitutionalDirection.UNKNOWN
    )


@pytest.mark.parametrize(
    "domain",
    [
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
def test_disabled_result_resolves_unknown(
    domain: str,
) -> None:
    assert (
        resolve(
            domain=domain,
            opinion="Bullish.",
            enabled=False,
        )
        is InstitutionalDirection.UNKNOWN
    )


def test_rejects_invalid_result_type() -> None:
    resolver = ExtendedBiasDirectionResolver()

    with pytest.raises(
        TypeError,
        match="result must be an AnalystResult or None",
    ):
        resolver.resolve(
            domain="AUCTION",
            result=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "domain",
    [
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
@pytest.mark.parametrize(
    "direction",
    [
        "bullish",
        "long",
        "up",
        "upward",
    ],
)
def test_payload_direction_resolves_bullish(
    domain: str,
    direction: str,
) -> None:
    assert (
        resolve(
            domain=domain,
            opinion="Unknown.",
            payload=StubPayload(
                direction=direction
            ),
        )
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "domain",
    [
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ],
)
@pytest.mark.parametrize(
    "direction",
    [
        "bearish",
        "short",
        "down",
        "downward",
    ],
)
def test_payload_direction_resolves_bearish(
    domain: str,
    direction: str,
) -> None:
    assert (
        resolve(
            domain=domain,
            opinion="Unknown.",
            payload=StubPayload(
                direction=direction
            ),
        )
        is InstitutionalDirection.BEARISH
    )


def test_auction_buyers_control_is_bullish() -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion="Buyers are in control.",
        )
        is InstitutionalDirection.BULLISH
    )


def test_auction_sellers_control_is_bearish() -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion="Sellers are in control.",
        )
        is InstitutionalDirection.BEARISH
    )


def test_auction_acceptance_higher_is_bullish() -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion="Higher prices accepted.",
        )
        is InstitutionalDirection.BULLISH
    )


def test_auction_acceptance_lower_is_bearish() -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion="Lower prices accepted.",
        )
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Auction discovery.",
        "Discovery phase.",
        "Two-sided auction.",
        "No auction control.",
    ],
)
def test_auction_neutral_context(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion=opinion,
        )
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Buying pressure remains active.",
        "Buy pressure remains active.",
        "Buyers applying pressure.",
        "Selling pressure exhausted.",
        "Seller exhaustion confirmed.",
    ],
)
def test_bullish_pressure(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="PRESSURE",
            opinion=opinion,
        )
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Selling pressure remains active.",
        "Sell pressure remains active.",
        "Sellers applying pressure.",
        "Buying pressure exhausted.",
        "Buyer exhaustion confirmed.",
    ],
)
def test_bearish_pressure(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="PRESSURE",
            opinion=opinion,
        )
        is InstitutionalDirection.BEARISH
    )


def test_balanced_pressure_is_neutral() -> None:
    assert (
        resolve(
            domain="PRESSURE",
            opinion="Balanced pressure.",
        )
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Bullish participation confirmed.",
        "Buyer participation remains strong.",
        "Participation supports buyers.",
        "Participation supports upside.",
        "Volume supports buyers.",
    ],
)
def test_bullish_participation(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="PARTICIPATION",
            opinion=opinion,
        )
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Bearish participation confirmed.",
        "Seller participation remains strong.",
        "Participation supports sellers.",
        "Participation supports downside.",
        "Volume supports sellers.",
    ],
)
def test_bearish_participation(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="PARTICIPATION",
            opinion=opinion,
        )
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Strong participation.",
        "Weak participation.",
        "Increasing participation.",
        "Decreasing participation.",
        "No directional participation.",
    ],
)
def test_non_directional_participation_is_neutral(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="PARTICIPATION",
            opinion=opinion,
        )
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Price is below value.",
        "Price is below fair value.",
        "Price is at discount.",
        "Market remains undervalued.",
        "Value support remains active.",
        "Price reclaimed value.",
    ],
)
def test_bullish_value_context(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="VALUE",
            opinion=opinion,
        )
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Price is above value.",
        "Price is above fair value.",
        "Price is at premium.",
        "Market remains overvalued.",
        "Value resistance remains active.",
        "Price rejected value.",
    ],
)
def test_bearish_value_context(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="VALUE",
            opinion=opinion,
        )
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "Price is at fair value.",
        "Price remains inside value.",
        "Value acceptance.",
        "Value remains balanced.",
    ],
)
def test_neutral_value_context(
    opinion: str,
) -> None:
    assert (
        resolve(
            domain="VALUE",
            opinion=opinion,
        )
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    (
        "domain",
        "opinion",
    ),
    [
        (
            "AUCTION",
            "Auction context unavailable.",
        ),
        (
            "PRESSURE",
            "No pressure data.",
        ),
        (
            "PARTICIPATION",
            "Participation not evaluated.",
        ),
        (
            "VALUE",
            "Value remains unresolved.",
        ),
    ],
)
def test_unknown_context(
    domain: str,
    opinion: str,
) -> None:
    assert (
        resolve(
            domain=domain,
            opinion=opinion,
        )
        is InstitutionalDirection.UNKNOWN
    )


def test_explicit_bullish_and_bearish_is_unknown() -> None:
    assert (
        resolve(
            domain="PRESSURE",
            opinion=(
                "Bullish pressure conflicts with bearish pressure."
            ),
        )
        is InstitutionalDirection.UNKNOWN
    )


def test_generic_buying_and_selling_pressure_is_unknown() -> None:
    assert (
        resolve(
            domain="PRESSURE",
            opinion=(
                "Buying pressure and selling pressure are active."
            ),
        )
        is InstitutionalDirection.UNKNOWN
    )


@pytest.mark.parametrize(
    "domain",
    [
        "",
        " ",
    ],
)
def test_rejects_empty_domain(
    domain: str,
) -> None:
    resolver = ExtendedBiasDirectionResolver()

    with pytest.raises(
        ValueError,
        match="domain cannot be empty",
    ):
        resolver.resolve(
            domain=domain,
            result=None,
        )


def test_rejects_non_string_domain() -> None:
    resolver = ExtendedBiasDirectionResolver()

    with pytest.raises(
        TypeError,
        match="domain must be a string",
    ):
        resolver.resolve(
            domain=123,  # type: ignore[arg-type]
            result=None,
        )


def test_rejects_unsupported_domain() -> None:
    resolver = ExtendedBiasDirectionResolver()

    with pytest.raises(
        KeyError,
        match=(
            "Unsupported extended bias domain: TREND"
        ),
    ):
        resolver.resolve(
            domain="TREND",
            result=None,
        )


def test_payload_has_priority_over_opinion() -> None:
    assert (
        resolve(
            domain="AUCTION",
            opinion="Sellers are in control.",
            payload=StubPayload(
                direction="bullish"
            ),
        )
        is InstitutionalDirection.BULLISH
    )


def test_unresolved_payload_falls_back_to_opinion() -> None:
    assert (
        resolve(
            domain="VALUE",
            opinion="Price is below fair value.",
            payload=StubPayload(
                direction="unknown",
                state="unresolved",
            ),
        )
        is InstitutionalDirection.BULLISH
    )


def test_resolver_is_frozen() -> None:
    resolver = ExtendedBiasDirectionResolver()

    with pytest.raises(
        AttributeError
    ):
        resolver.new_value = True  # type: ignore[attr-defined]