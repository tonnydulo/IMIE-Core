from __future__ import annotations

from enum import StrEnum


class MarketSessionState(StrEnum):
    PREMARKET = "PREMARKET"
    REGULAR_SESSION = "REGULAR_SESSION"
    AFTER_HOURS = "AFTER_HOURS"
    CLOSED = "CLOSED"