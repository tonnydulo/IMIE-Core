from __future__ import annotations

from enum import Enum


class OrderBlockSide(str, Enum):
    """
    Directional side of an institutional order block.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class OrderBlockState(str, Enum):
    """
    Runtime lifecycle state of an order block.
    """

    ACTIVE = "ACTIVE"
    TESTED = "TESTED"
    MITIGATED = "MITIGATED"
    BROKEN = "BROKEN"
    RETIRED = "RETIRED"


class OrderBlockImportance(str, Enum):
    """
    Institutional importance assigned to an order block.
    """

    MINOR = "MINOR"
    INTERMEDIATE = "INTERMEDIATE"
    MAJOR = "MAJOR"


class OrderBlockOrigin(str, Enum):
    """
    Market event that caused the order block to be recognized.
    """

    BOS = "BOS"
    CHOCH = "CHOCH"
    MSS = "MSS"
    DISPLACEMENT = "DISPLACEMENT"
    UNCLASSIFIED = "UNCLASSIFIED"