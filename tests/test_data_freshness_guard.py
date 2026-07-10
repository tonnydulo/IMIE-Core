from datetime import datetime, timedelta, timezone

from imie.models import MarketBar, MarketSnapshot, Quote
from imie.services import DataFreshnessGuard


def build_snapshot(
    *,
    checked_at: datetime,
    quote_age_seconds: int,
    bar_age_seconds: int,
) -> MarketSnapshot:
    quote = Quote(
        symbol="TEST",
        timestamp=checked_at - timedelta(seconds=quote_age_seconds),
        bid=100.00,
        ask=100.02,
        last=100.01,
        provider="test",
    )

    bar = MarketBar(
        symbol="TEST",
        timestamp=checked_at - timedelta(seconds=bar_age_seconds),
        open=99.80,
        high=100.10,
        low=99.70,
        close=100.00,
        volume=10_000,
        timeframe="2m",
        provider="test",
    )

    return MarketSnapshot(
        symbol="TEST",
        timestamp=quote.timestamp,
        quote=quote,
        bars=[bar],
        timeframe="2m",
    )


def test_fresh_aligned_data_is_actionable() -> None:
    checked_at = datetime(2026, 7, 9, 15, 0, tzinfo=timezone.utc)
    snapshot = build_snapshot(
        checked_at=checked_at,
        quote_age_seconds=10,
        bar_age_seconds=130,
    )

    guard = DataFreshnessGuard()
    result = guard.evaluate(snapshot, checked_at=checked_at)

    assert result.actionable is True
    assert result.status == "FRESH"
    assert result.quote_is_fresh is True
    assert result.bar_is_fresh is True
    assert result.timestamps_aligned is True


def test_stale_quote_is_not_actionable() -> None:
    checked_at = datetime(2026, 7, 9, 15, 0, tzinfo=timezone.utc)
    snapshot = build_snapshot(
        checked_at=checked_at,
        quote_age_seconds=120,
        bar_age_seconds=130,
    )

    guard = DataFreshnessGuard()
    result = guard.evaluate(snapshot, checked_at=checked_at)

    assert result.actionable is False
    assert result.quote_is_fresh is False
    assert "quote is stale" in result.reason.lower()


def test_stale_bar_is_not_actionable() -> None:
    checked_at = datetime(2026, 7, 9, 15, 0, tzinfo=timezone.utc)
    snapshot = build_snapshot(
        checked_at=checked_at,
        quote_age_seconds=10,
        bar_age_seconds=600,
    )

    guard = DataFreshnessGuard()
    result = guard.evaluate(snapshot, checked_at=checked_at)

    assert result.actionable is False
    assert result.bar_is_fresh is False
    assert "bar is stale" in result.reason.lower()


def test_misaligned_quote_and_bar_are_not_actionable() -> None:
    checked_at = datetime(2026, 7, 9, 15, 0, tzinfo=timezone.utc)
    snapshot = build_snapshot(
        checked_at=checked_at,
        quote_age_seconds=10,
        bar_age_seconds=400,
    )

    guard = DataFreshnessGuard(
        max_bar_age_seconds=600,
        max_quote_bar_gap_seconds=300,
    )
    result = guard.evaluate(snapshot, checked_at=checked_at)

    assert result.actionable is False
    assert result.bar_is_fresh is True
    assert result.timestamps_aligned is False
    assert "misaligned" in result.reason.lower()
