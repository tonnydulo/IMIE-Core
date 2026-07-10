from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DataFreshness:
    checked_at: datetime
    quote_timestamp: datetime
    latest_bar_timestamp: datetime
    quote_age_seconds: float
    bar_age_seconds: float
    quote_bar_gap_seconds: float
    quote_is_fresh: bool
    bar_is_fresh: bool
    timestamps_aligned: bool
    actionable: bool
    status: str
    reason: str
