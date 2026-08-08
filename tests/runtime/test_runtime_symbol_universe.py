import pytest

from imie.runtime.runtime_symbol_universe import (
    RuntimeSymbolUniverse,
)


def test_symbols_are_normalized() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            " nvda ",
            "amd",
            " SPY ",
        )
    )

    assert universe.symbols == (
        "NVDA",
        "AMD",
        "SPY",
    )


def test_duplicate_symbols_are_removed_in_order() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "nvda",
            "SPY",
            "amd",
        )
    )

    assert universe.symbols == (
        "NVDA",
        "AMD",
        "SPY",
    )


def test_symbols_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="symbols must be a tuple",
    ):
        RuntimeSymbolUniverse(
            symbols=["NVDA", "AMD"],  # type: ignore[arg-type]
        )


def test_symbols_cannot_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="symbols cannot be empty",
    ):
        RuntimeSymbolUniverse(
            symbols=(),
        )


def test_each_symbol_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="each symbol must be a string",
    ):
        RuntimeSymbolUniverse(
            symbols=(
                "NVDA",
                123,  # type: ignore[arg-type]
            )
        )


def test_symbol_values_cannot_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="empty values",
    ):
        RuntimeSymbolUniverse(
            symbols=(
                "NVDA",
                " ",
            )
        )


def test_len_returns_unique_symbol_count() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "nvda",
        )
    )

    assert len(
        universe
    ) == 2


def test_iteration_preserves_symbol_order() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    assert tuple(
        universe
    ) == (
        "NVDA",
        "AMD",
        "SPY",
    )


def test_contains_normalizes_lookup_symbol() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
        )
    )

    assert " nvda " in universe
    assert "AMD" in universe
    assert "SPY" not in universe
    assert 123 not in universe