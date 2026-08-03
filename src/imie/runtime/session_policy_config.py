from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SessionPolicyConfig:
    """
    Controls which market sessions may run IMIE analysis.
    """

    allow_premarket: bool = True
    allow_regular_session: bool = True
    allow_after_hours: bool = False
    allow_closed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "allow_premarket",
            "allow_regular_session",
            "allow_after_hours",
            "allow_closed",
        ):
            if not isinstance(
                getattr(
                    self,
                    name,
                ),
                bool,
            ):
                raise TypeError(
                    f"{name} must be a bool."
                )