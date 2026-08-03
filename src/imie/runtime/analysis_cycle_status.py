from __future__ import annotations

from enum import Enum


class AnalysisCycleStatus(str, Enum):
    COMPLETED = "COMPLETED"
    SKIPPED_NO_NEW_BAR = "SKIPPED_NO_NEW_BAR"
    SKIPPED_SESSION = "SKIPPED_SESSION"
    STALE_DATA = "STALE_DATA"
    FAILED = "FAILED"