from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Swing:
    """
    Represents a confirmed market swing.

    A Swing is the smallest unit of market structure.
    StructureAnalyst builds its structural map from Swing objects.
    """

    index: int
    price: float
    kind: str
    strength: int

    def __post_init__(self) -> None:
        if self.kind not in {"HIGH", "LOW"}:
            raise ValueError(
                "Swing kind must be HIGH or LOW."
            )

        if self.strength < 1:
            raise ValueError(
                "Swing strength must be at least 1."
            )

        object.__setattr__(
            self,
            "kind",
            self.kind.upper(),
        )