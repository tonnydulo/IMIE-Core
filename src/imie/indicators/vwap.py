from datetime import time
from zoneinfo import ZoneInfo

from imie.models import MarketBar


NEW_YORK = ZoneInfo("America/New_York")

REGULAR_SESSION_START = time(9, 30)
REGULAR_SESSION_END = time(16, 0)

EXTENDED_SESSION_START = time(4, 0)
EXTENDED_SESSION_END = time(20, 0)


def calculate_vwap(
    bars: list[MarketBar],
    *,
    include_extended_hours: bool = False,
) -> float | None:
    """
    Calculate session-reset VWAP for the most recent trading date in `bars`.

    Regular-hours mode:
        09:30 <= timestamp < 16:00 America/New_York

    Extended-hours mode:
        04:00 <= timestamp < 20:00 America/New_York
    """
    session_bars = filter_current_session_bars(
        bars,
        include_extended_hours=include_extended_hours,
    )

    total_price_volume = 0.0
    total_volume = 0

    for bar in session_bars:
        if bar.volume <= 0:
            continue

        typical_price = (bar.high + bar.low + bar.close) / 3.0
        total_price_volume += typical_price * bar.volume
        total_volume += bar.volume

    if total_volume == 0:
        return None

    return total_price_volume / total_volume


def filter_current_session_bars(
    bars: list[MarketBar],
    *,
    include_extended_hours: bool = False,
) -> list[MarketBar]:
    if not bars:
        return []

    localized_bars = [
        (bar, _to_new_york(bar))
        for bar in bars
    ]

    latest_trading_date = max(
        localized_timestamp.date()
        for _, localized_timestamp in localized_bars
    )

    if include_extended_hours:
        session_start = EXTENDED_SESSION_START
        session_end = EXTENDED_SESSION_END
    else:
        session_start = REGULAR_SESSION_START
        session_end = REGULAR_SESSION_END

    return [
        bar
        for bar, localized_timestamp in localized_bars
        if localized_timestamp.date() == latest_trading_date
        and session_start <= localized_timestamp.time() < session_end
    ]


def _to_new_york(bar: MarketBar):
    timestamp = bar.timestamp

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))

    return timestamp.astimezone(NEW_YORK)
