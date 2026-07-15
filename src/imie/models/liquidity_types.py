from __future__ import annotations

from enum import Enum

class LiquidityBias(str, Enum):
    """
    Institutional liquidity bias determined from
    the current liquidity landscape.
    """

    UNKNOWN = "UNKNOWN"

    BALANCED = "BALANCED"

    BUY_SIDE_DOMINANT = "BUY_SIDE_DOMINANT"

    SELL_SIDE_DOMINANT = "SELL_SIDE_DOMINANT"
     
class LiquiditySide(str, Enum):
    """The side of the market where liquidity is resting."""

    BUY_SIDE = "buy_side"
    SELL_SIDE = "sell_side"


class LiquidityType(str, Enum):
    """The source or structural form of a liquidity level."""

    EQUAL_HIGH = "equal_high"
    EQUAL_LOW = "equal_low"

    PREVIOUS_DAY_HIGH = "previous_day_high"
    PREVIOUS_DAY_LOW = "previous_day_low"

    PREVIOUS_WEEK_HIGH = "previous_week_high"
    PREVIOUS_WEEK_LOW = "previous_week_low"

    OPENING_RANGE_HIGH = "opening_range_high"
    OPENING_RANGE_LOW = "opening_range_low"

    PREMARKET_HIGH = "premarket_high"
    PREMARKET_LOW = "premarket_low"

    LONDON_HIGH = "london_high"
    LONDON_LOW = "london_low"

    TOKYO_HIGH = "tokyo_high"
    TOKYO_LOW = "tokyo_low"

    INTERNAL_SWING_HIGH = "internal_swing_high"
    INTERNAL_SWING_LOW = "internal_swing_low"

    EXTERNAL_SWING_HIGH = "external_swing_high"
    EXTERNAL_SWING_LOW = "external_swing_low"


class LiquidityImportance(str, Enum):
    """Institutional significance of a liquidity source."""

    MAJOR = "major"
    INTERMEDIATE = "intermediate"
    MINOR = "minor"


class LiquidityLocation(str, Enum):
    """Whether liquidity exists inside or outside the active structure."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    UNCLASSIFIED = "unclassified"


class LiquidityState(str, Enum):
    """Current lifecycle state of a liquidity level or pool."""

    ACTIVE = "active"
    TESTED = "tested"
    SWEPT = "swept"
    CONSUMED = "consumed"
    INVALIDATED = "invalidated"


class SweepDirection(str, Enum):
    """Direction implied by a confirmed liquidity sweep."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NONE = "none"

class LiquidityPoolStateType(str, Enum):
    """
    Lifecycle state of an institutional liquidity pool.
    """

    ACTIVE = "ACTIVE"

    SWEPT = "SWEPT"

    RETESTED = "RETESTED"

    CONSUMED = "CONSUMED"

    RETIRED = "RETIRED"