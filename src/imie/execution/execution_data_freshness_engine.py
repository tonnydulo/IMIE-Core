from __future__ import annotations

from imie.models import DataFreshness, ExecutionDataFreshnessAssessment


class ExecutionDataFreshnessEngine:
    """Require verified actionable market-data truth before execution."""

    def assess(
        self,
        freshness: DataFreshness,
    ) -> ExecutionDataFreshnessAssessment:
        if not isinstance(freshness, DataFreshness):
            raise TypeError("freshness must be a DataFreshness.")

        violations = []
        if freshness.quote_is_fresh is not True:
            violations.append("Market quote is stale.")
        if freshness.bar_is_fresh is not True:
            violations.append("Latest market bar is stale.")
        if freshness.timestamps_aligned is not True:
            violations.append("Quote and bar timestamps are not aligned.")
        if freshness.actionable is not True and not violations:
            violations.append(
                "Data freshness guard did not authorize execution: "
                f"{freshness.reason}"
            )
        allowed = (
            freshness.actionable is True
            and freshness.quote_is_fresh is True
            and freshness.bar_is_fresh is True
            and freshness.timestamps_aligned is True
        )
        return ExecutionDataFreshnessAssessment(
            checked_at=freshness.checked_at,
            quote_timestamp=freshness.quote_timestamp,
            latest_bar_timestamp=freshness.latest_bar_timestamp,
            quote_age_seconds=freshness.quote_age_seconds,
            bar_age_seconds=freshness.bar_age_seconds,
            quote_bar_gap_seconds=freshness.quote_bar_gap_seconds,
            quote_is_fresh=freshness.quote_is_fresh,
            bar_is_fresh=freshness.bar_is_fresh,
            timestamps_aligned=freshness.timestamps_aligned,
            source_actionable=freshness.actionable,
            allowed=allowed,
            status=freshness.status,
            reason=freshness.reason,
            violations=tuple(violations),
        )
