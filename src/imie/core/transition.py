from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class Transition(Generic[StateT]):
    """
    Immutable description of a legal state transition.

    The Transition object contains no business logic.
    It simply describes movement from one state to another.
    """

    previous: StateT

    current: StateT

    reason: str

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]

    def __post_init__(self) -> None:

        if not self.reason.strip():
            raise ValueError(
                "Transition reason cannot be empty."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.evidence
        ):
            raise ValueError(
                "Transition evidence entries must be "
                "non-empty strings."
            )

        if any(
            not isinstance(item, str)
            or not item.strip()
            for item in self.warnings
        ):
            raise ValueError(
                "Transition warning entries must be "
                "non-empty strings."
            )