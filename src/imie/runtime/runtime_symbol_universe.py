from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeSymbolUniverse:
    """
    Ordered collection of unique market symbols for runtime analysis.

    Symbols are normalized by trimming surrounding whitespace and
    converting to uppercase. Duplicate symbols are removed while
    preserving their first-seen order.
    """

    symbols: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.symbols,
            tuple,
        ):
            raise TypeError(
                "symbols must be a tuple."
            )

        if not self.symbols:
            raise ValueError(
                "symbols cannot be empty."
            )

        normalized: list[str] = []
        seen: set[str] = set()

        for value in self.symbols:
            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    "each symbol must be a string."
                )

            symbol = value.strip().upper()

            if not symbol:
                raise ValueError(
                    "symbols cannot contain empty values."
                )

            if symbol in seen:
                continue

            seen.add(
                symbol
            )

            normalized.append(
                symbol
            )

        object.__setattr__(
            self,
            "symbols",
            tuple(
                normalized
            ),
        )

    def __len__(self) -> int:
        return len(
            self.symbols
        )

    def __iter__(self):
        return iter(
            self.symbols
        )

    def __contains__(
        self,
        symbol: object,
    ) -> bool:
        if not isinstance(
            symbol,
            str,
        ):
            return False

        return (
            symbol.strip().upper()
            in self.symbols
        )