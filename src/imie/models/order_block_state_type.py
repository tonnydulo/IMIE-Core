from __future__ import annotations

from enum import Enum


class OrderBlockStateType(str, Enum):
    """
    Lifecycle state of an institutional order block.
    """

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    TESTED = "TESTED"
    MITIGATED = "MITIGATED"
    INVALIDATED = "INVALIDATED"