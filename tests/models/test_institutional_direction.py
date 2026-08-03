from __future__ import annotations

import pytest

from imie.models import (
    InstitutionalDirection,
)


def test_enum_values() -> None:
    assert (
        InstitutionalDirection.BULLISH.value
        == "BULLISH"
    )
    assert (
        InstitutionalDirection.BEARISH.value
        == "BEARISH"
    )
    assert (
        InstitutionalDirection.NEUTRAL.value
        == "NEUTRAL"
    )
    assert (
        InstitutionalDirection.UNKNOWN.value
        == "UNKNOWN"
    )


def test_enum_is_string_compatible() -> None:
    assert isinstance(
        InstitutionalDirection.BULLISH,
        str,
    )


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            True,
        ),
        (
            InstitutionalDirection.BEARISH,
            False,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            False,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            False,
        ),
    ],
)
def test_is_bullish(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_bullish is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            False,
        ),
        (
            InstitutionalDirection.BEARISH,
            True,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            False,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            False,
        ),
    ],
)
def test_is_bearish(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_bearish is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            False,
        ),
        (
            InstitutionalDirection.BEARISH,
            False,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            True,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            False,
        ),
    ],
)
def test_is_neutral(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_neutral is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            False,
        ),
        (
            InstitutionalDirection.BEARISH,
            False,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            False,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            True,
        ),
    ],
)
def test_is_unknown(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_unknown is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            True,
        ),
        (
            InstitutionalDirection.BEARISH,
            True,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            False,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            False,
        ),
    ],
)
def test_is_directional(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_directional is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            True,
        ),
        (
            InstitutionalDirection.BEARISH,
            True,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            True,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            False,
        ),
    ],
)
def test_is_resolved(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_resolved is expected


@pytest.mark.parametrize(
    (
        "direction",
        "expected",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            False,
        ),
        (
            InstitutionalDirection.BEARISH,
            False,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            True,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            True,
        ),
    ],
)
def test_is_non_directional(
    direction: InstitutionalDirection,
    expected: bool,
) -> None:
    assert direction.is_non_directional is expected


def test_bullish_opposes_bearish() -> None:
    assert (
        InstitutionalDirection.BULLISH.opposes(
            InstitutionalDirection.BEARISH
        )
        is True
    )


def test_bearish_opposes_bullish() -> None:
    assert (
        InstitutionalDirection.BEARISH.opposes(
            InstitutionalDirection.BULLISH
        )
        is True
    )


@pytest.mark.parametrize(
    (
        "left",
        "right",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            InstitutionalDirection.BULLISH,
        ),
        (
            InstitutionalDirection.BEARISH,
            InstitutionalDirection.BEARISH,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            InstitutionalDirection.BULLISH,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            InstitutionalDirection.BEARISH,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            InstitutionalDirection.UNKNOWN,
        ),
    ],
)
def test_non_opposing_combinations(
    left: InstitutionalDirection,
    right: InstitutionalDirection,
) -> None:
    assert left.opposes(
        right
    ) is False


def test_opposes_rejects_invalid_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "other must be an "
            "InstitutionalDirection"
        ),
    ):
        InstitutionalDirection.BULLISH.opposes(
            "BEARISH"  # type: ignore[arg-type]
        )


def test_bullish_aligns_with_bullish() -> None:
    assert (
        InstitutionalDirection.BULLISH.aligns_with(
            InstitutionalDirection.BULLISH
        )
        is True
    )


def test_bearish_aligns_with_bearish() -> None:
    assert (
        InstitutionalDirection.BEARISH.aligns_with(
            InstitutionalDirection.BEARISH
        )
        is True
    )


@pytest.mark.parametrize(
    (
        "left",
        "right",
    ),
    [
        (
            InstitutionalDirection.BULLISH,
            InstitutionalDirection.BEARISH,
        ),
        (
            InstitutionalDirection.BEARISH,
            InstitutionalDirection.BULLISH,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            InstitutionalDirection.NEUTRAL,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            InstitutionalDirection.UNKNOWN,
        ),
        (
            InstitutionalDirection.NEUTRAL,
            InstitutionalDirection.BULLISH,
        ),
        (
            InstitutionalDirection.UNKNOWN,
            InstitutionalDirection.BEARISH,
        ),
    ],
)
def test_non_aligning_combinations(
    left: InstitutionalDirection,
    right: InstitutionalDirection,
) -> None:
    assert left.aligns_with(
        right
    ) is False


def test_aligns_with_rejects_invalid_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "other must be an "
            "InstitutionalDirection"
        ),
    ):
        InstitutionalDirection.BULLISH.aligns_with(
            "BULLISH"  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [
        InstitutionalDirection.BULLISH,
        "BULLISH",
        "bullish",
        " bullish ",
        "BULL",
        "bull",
        "LONG",
        "long",
        "UP",
        "upward",
    ],
)
def test_from_value_resolves_bullish(
    value: object,
) -> None:
    assert (
        InstitutionalDirection.from_value(
            value
        )
        is InstitutionalDirection.BULLISH
    )


@pytest.mark.parametrize(
    "value",
    [
        InstitutionalDirection.BEARISH,
        "BEARISH",
        "bearish",
        " bearish ",
        "BEAR",
        "bear",
        "SHORT",
        "short",
        "DOWN",
        "downward",
    ],
)
def test_from_value_resolves_bearish(
    value: object,
) -> None:
    assert (
        InstitutionalDirection.from_value(
            value
        )
        is InstitutionalDirection.BEARISH
    )


@pytest.mark.parametrize(
    "value",
    [
        InstitutionalDirection.NEUTRAL,
        "NEUTRAL",
        "neutral",
        "BALANCED",
        "balanced",
        "BALANCE",
    ],
)
def test_from_value_resolves_neutral(
    value: object,
) -> None:
    assert (
        InstitutionalDirection.from_value(
            value
        )
        is InstitutionalDirection.NEUTRAL
    )


@pytest.mark.parametrize(
    "value",
    [
        InstitutionalDirection.UNKNOWN,
        "UNKNOWN",
        "unknown",
        "NONE",
        "UNAVAILABLE",
        "UNRESOLVED",
        "",
        " ",
        None,
        object(),
        "sideways",
    ],
)
def test_from_value_resolves_unknown(
    value: object,
) -> None:
    assert (
        InstitutionalDirection.from_value(
            value
        )
        is InstitutionalDirection.UNKNOWN
    )


def test_from_value_returns_same_enum_instance() -> None:
    result = InstitutionalDirection.from_value(
        InstitutionalDirection.BULLISH
    )

    assert (
        result
        is InstitutionalDirection.BULLISH
    )


def test_enum_members_are_unique() -> None:
    assert len(
        set(
            InstitutionalDirection
        )
    ) == 4