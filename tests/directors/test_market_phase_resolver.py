from __future__ import annotations

import pytest

from imie.directors.market_phase_resolver import (
    MarketPhaseResolver,
)
from imie.models import (
    AnalystResult,
    MarketPhaseType,
)
from dataclasses import dataclass


@pytest.fixture
def resolver() -> MarketPhaseResolver:
    return MarketPhaseResolver()


def make_result(
    *,
    payload: object = None,
    enabled: bool = True,
) -> AnalystResult:
    return AnalystResult(
        analyst="TestAnalyst",
        opinion="Market phase test result.",
        confidence=80.0,
        evidence=(),
        warnings=(),
        payload={} if payload is None else payload,
        enabled=enabled,
    )


def test_none_result_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    result = resolver.resolve(
        None
    )

    assert result is MarketPhaseType.UNKNOWN


def test_disabled_result_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": "MARKUP",
        },
        enabled=False,
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.UNKNOWN


def test_non_dictionary_payload_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload="MARKUP"
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.UNKNOWN


def test_missing_market_phase_key_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "direction": "BULLISH",
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.UNKNOWN


def test_none_market_phase_value_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": None,
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.UNKNOWN


def test_invalid_market_phase_string_resolves_unknown(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": "INVALID_PHASE",
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.UNKNOWN


def test_valid_enum_phase_is_returned(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": MarketPhaseType.MARKUP,
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.MARKUP


def test_lowercase_phase_string_is_normalized(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": "markup",
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.MARKUP


def test_mixed_case_phase_string_is_normalized(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": "Expansion",
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.EXPANSION


def test_phase_string_whitespace_is_removed(
    resolver: MarketPhaseResolver,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": "  pullback  ",
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is MarketPhaseType.PULLBACK


@pytest.mark.parametrize(
    ("phase", "expected"),
    (
        ("UNKNOWN", MarketPhaseType.UNKNOWN),
        ("ACCUMULATION", MarketPhaseType.ACCUMULATION),
        ("MARKUP", MarketPhaseType.MARKUP),
        ("PULLBACK", MarketPhaseType.PULLBACK),
        ("EXPANSION", MarketPhaseType.EXPANSION),
        ("DISTRIBUTION", MarketPhaseType.DISTRIBUTION),
        ("MARKDOWN", MarketPhaseType.MARKDOWN),
        ("COMPRESSION", MarketPhaseType.COMPRESSION),
        ("REVERSAL", MarketPhaseType.REVERSAL),
        ("TRANSITION", MarketPhaseType.TRANSITION),
    ),
)
def test_all_valid_phase_strings_resolve(
    resolver: MarketPhaseResolver,
    phase: str,
    expected: MarketPhaseType,
) -> None:
    analyst_result = make_result(
        payload={
            "market_phase": phase,
        }
    )

    result = resolver.resolve(
        analyst_result
    )

    assert result is expected

@dataclass(frozen=True, slots=True)
class TypedPhasePayload:
    market_phase: MarketPhaseType


def test_resolves_market_phase_from_typed_payload() -> None:
    resolver = MarketPhaseResolver()

    result = AnalystResult(
        analyst="AuctionAnalyst",
        analyst_id="AUCTION",
        opinion="Buyers control the auction.",
        confidence=85.0,
        evidence=[],
        warnings=[],
        payload=TypedPhasePayload(
            market_phase=MarketPhaseType.MARKUP,
        ),
        enabled=True,
    )

    assert (
        resolver.resolve(result)
        is MarketPhaseType.MARKUP
    )