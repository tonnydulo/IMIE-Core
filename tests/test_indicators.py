from datetime import datetime, timezone

import pytest

from imie.indicators import (
    calculate_atr_wilder,
    calculate_ema,
    calculate_vwap,
)
from imie.models import MarketBar


def make_bar(
    timestamp: datetime,
    close: float,
    *,
    high: float | None = None,
    low: float | None = None,
    volume: int = 100,
) -> MarketBar:
    resolved_high = high if high is not None else close + 0.50
    resolved_low = low if low is not None else close - 0.50

    return MarketBar(
        symbol="TEST",
        timestamp=timestamp,
        open=close,
        high=resolved_high,
        low=resolved_low,
        close=close,
        volume=volume,
        timeframe="2m",
        provider="test",
    )


def test_ema_first_value_seed() -> None:
    bars = [
        make_bar(datetime(2026, 7, 9, 13, 30, tzinfo=timezone.utc), 10.0),
        make_bar(datetime(2026, 7, 9, 13, 32, tzinfo=timezone.utc), 11.0),
        make_bar(datetime(2026, 7, 9, 13, 34, tzinfo=timezone.utc), 12.0),
    ]

    result = calculate_ema(bars, period=3, seed_method="first")

    # Alpha = 0.5: 10.0 -> 10.5 -> 11.25
    assert result == pytest.approx(11.25)


def test_vwap_resets_to_latest_regular_session() -> None:
    bars = [
        # Previous session. This must not influence the result.
        make_bar(
            datetime(2026, 7, 8, 14, 30, tzinfo=timezone.utc),
            50.0,
            volume=1_000,
        ),
        # Current session at 09:30 and 09:32 ET.
        make_bar(
            datetime(2026, 7, 9, 13, 30, tzinfo=timezone.utc),
            100.0,
            high=101.0,
            low=99.0,
            volume=100,
        ),
        make_bar(
            datetime(2026, 7, 9, 13, 32, tzinfo=timezone.utc),
            103.0,
            high=104.0,
            low=102.0,
            volume=300,
        ),
    ]

    result = calculate_vwap(
        bars,
        include_extended_hours=False,
    )

    # ((100 * 100) + (103 * 300)) / 400 = 102.25
    assert result == pytest.approx(102.25)


def test_regular_vwap_excludes_premarket() -> None:
    bars = [
        # 08:00 ET. Excluded from regular-hours VWAP.
        make_bar(
            datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc),
            50.0,
            volume=10_000,
        ),
        # 09:30 ET. Included in regular-hours VWAP.
        make_bar(
            datetime(2026, 7, 9, 13, 30, tzinfo=timezone.utc),
            100.0,
            volume=100,
        ),
    ]

    result = calculate_vwap(
        bars,
        include_extended_hours=False,
    )

    assert result == pytest.approx(100.0)


def test_extended_vwap_includes_premarket() -> None:
    bars = [
        # 08:00 ET.
        make_bar(
            datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc),
            80.0,
            volume=100,
        ),
        # 09:30 ET.
        make_bar(
            datetime(2026, 7, 9, 13, 30, tzinfo=timezone.utc),
            100.0,
            volume=100,
        ),
    ]

    result = calculate_vwap(
        bars,
        include_extended_hours=True,
    )

    assert result == pytest.approx(90.0)


def test_wilder_atr_constant_true_range() -> None:
    bars = [
        make_bar(
            datetime(2026, 7, 9, 13, 30 + index, tzinfo=timezone.utc),
            100.0,
            high=101.0,
            low=99.0,
        )
        for index in range(16)
    ]

    result = calculate_atr_wilder(bars, period=14)

    assert result == pytest.approx(2.0)
