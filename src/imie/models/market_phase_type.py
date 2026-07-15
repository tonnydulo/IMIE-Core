from __future__ import annotations

from enum import Enum


class MarketPhaseType(str, Enum):
    """
    Institutional auction phases.
    """

    UNKNOWN = "UNKNOWN"

    ACCUMULATION = "ACCUMULATION"

    MARKUP = "MARKUP"

    PULLBACK = "PULLBACK"

    EXPANSION = "EXPANSION"

    DISTRIBUTION = "DISTRIBUTION"

    MARKDOWN = "MARKDOWN"

    COMPRESSION = "COMPRESSION"

    REVERSAL = "REVERSAL"

    TRANSITION = "TRANSITION"

    @property
    def is_known(self) -> bool:
        return self is not MarketPhaseType.UNKNOWN

    @property
    def is_trending(self) -> bool:
        return self in (
            MarketPhaseType.MARKUP,
            MarketPhaseType.MARKDOWN,
            MarketPhaseType.EXPANSION,
        )

    @property
    def is_reversal(self) -> bool:
        return self is MarketPhaseType.REVERSAL

    @property
    def is_transition(self) -> bool:
        return self in (
            MarketPhaseType.TRANSITION,
            MarketPhaseType.PULLBACK,
            MarketPhaseType.DISTRIBUTION,
            MarketPhaseType.ACCUMULATION,
            MarketPhaseType.COMPRESSION,
        )