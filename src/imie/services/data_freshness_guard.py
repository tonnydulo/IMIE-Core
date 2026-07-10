from datetime import datetime, timezone

from imie.models import DataFreshness, MarketSnapshot


class DataFreshnessGuard:
    def __init__(
        self,
        *,
        max_quote_age_seconds: float = 60.0,
        max_bar_age_seconds: float = 300.0,
        max_quote_bar_gap_seconds: float = 300.0,
    ) -> None:
        if max_quote_age_seconds <= 0:
            raise ValueError("Maximum quote age must be greater than zero.")

        if max_bar_age_seconds <= 0:
            raise ValueError("Maximum bar age must be greater than zero.")

        if max_quote_bar_gap_seconds <= 0:
            raise ValueError("Maximum quote/bar gap must be greater than zero.")

        self.max_quote_age_seconds = max_quote_age_seconds
        self.max_bar_age_seconds = max_bar_age_seconds
        self.max_quote_bar_gap_seconds = max_quote_bar_gap_seconds

    def evaluate(
        self,
        snapshot: MarketSnapshot,
        *,
        checked_at: datetime | None = None,
    ) -> DataFreshness:
        if not snapshot.bars:
            raise ValueError("Cannot evaluate freshness without market bars.")

        resolved_checked_at = self._as_utc(
            checked_at if checked_at is not None else datetime.now(timezone.utc)
        )
        quote_timestamp = self._as_utc(snapshot.quote.timestamp)
        latest_bar_timestamp = self._as_utc(snapshot.bars[-1].timestamp)

        quote_age_seconds = max(
            0.0,
            (resolved_checked_at - quote_timestamp).total_seconds(),
        )
        bar_age_seconds = max(
            0.0,
            (resolved_checked_at - latest_bar_timestamp).total_seconds(),
        )
        quote_bar_gap_seconds = abs(
            (quote_timestamp - latest_bar_timestamp).total_seconds()
        )

        quote_is_fresh = quote_age_seconds <= self.max_quote_age_seconds
        bar_is_fresh = bar_age_seconds <= self.max_bar_age_seconds
        timestamps_aligned = (
            quote_bar_gap_seconds <= self.max_quote_bar_gap_seconds
        )
        actionable = quote_is_fresh and bar_is_fresh and timestamps_aligned

        status, reason = self._build_status(
            quote_is_fresh=quote_is_fresh,
            bar_is_fresh=bar_is_fresh,
            timestamps_aligned=timestamps_aligned,
        )

        return DataFreshness(
            checked_at=resolved_checked_at,
            quote_timestamp=quote_timestamp,
            latest_bar_timestamp=latest_bar_timestamp,
            quote_age_seconds=quote_age_seconds,
            bar_age_seconds=bar_age_seconds,
            quote_bar_gap_seconds=quote_bar_gap_seconds,
            quote_is_fresh=quote_is_fresh,
            bar_is_fresh=bar_is_fresh,
            timestamps_aligned=timestamps_aligned,
            actionable=actionable,
            status=status,
            reason=reason,
        )

    def _build_status(
        self,
        *,
        quote_is_fresh: bool,
        bar_is_fresh: bool,
        timestamps_aligned: bool,
    ) -> tuple[str, str]:
        failures: list[str] = []

        if not quote_is_fresh:
            failures.append("latest quote is stale")

        if not bar_is_fresh:
            failures.append("latest bar is stale")

        if not timestamps_aligned:
            failures.append("quote and bar timestamps are misaligned")

        if failures:
            return "STALE", "; ".join(failures).capitalize() + "."

        return "FRESH", "Quote and bar data are sufficiently synchronized."

    def _as_utc(self, timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)
