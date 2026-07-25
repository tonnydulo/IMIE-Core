from __future__ import annotations

from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)

from imie.runtime.market_session_clock import (
    MarketSessionClock,
)

from imie.runtime.session_policy import (
    SessionPolicy,
)
from imie.runtime.session_wake_result import (
    SessionWakeResult,
)


class SessionWakePlanner:
    """
    Calculates the next session boundary at which the configured
    SessionPolicy permits runtime analysis.
    """

    def __init__(
        self,
        *,
        market_session_clock: MarketSessionClock,
        session_policy: SessionPolicy,
        maximum_search_days: int = 14,
    ) -> None:
        if not isinstance(
            market_session_clock,
            MarketSessionClock,
        ):
            raise TypeError(
                "market_session_clock must be a "
                "MarketSessionClock."
            )

        if not isinstance(
            session_policy,
            SessionPolicy,
        ):
            raise TypeError(
                "session_policy must be a SessionPolicy."
            )

        if isinstance(
            maximum_search_days,
            bool,
        ) or not isinstance(
            maximum_search_days,
            int,
        ):
            raise TypeError(
                "maximum_search_days must be an int."
            )

        if maximum_search_days < 1:
            raise ValueError(
                "maximum_search_days must be at least 1."
            )

        self.market_session_clock = (
            market_session_clock
        )
        self.session_policy = session_policy
        self.maximum_search_days = (
            maximum_search_days
        )

    def evaluate(
        self,
        checked_at: datetime,
    ) -> SessionWakeResult:
        resolved_time = self._resolve_time(
            checked_at
        )

        market_time = resolved_time.astimezone(
            self.market_session_clock
            .config
            .timezone
        )

        for day_offset in range(
            self.maximum_search_days + 1
        ):
            candidate_date = (
                market_time.date()
                + timedelta(
                    days=day_offset
                )
            )

            candidates = self._candidate_times(
                candidate_date
            )

            for candidate in candidates:
                candidate_utc = candidate.astimezone(
                    timezone.utc
                )

                if candidate_utc <= resolved_time:
                    continue

                session_result = (
                    self.market_session_clock.evaluate(
                        candidate_utc
                    )
                )

                policy_result = (
                    self.session_policy.evaluate(
                        session_result
                    )
                )

                if policy_result.may_analyze:
                    delay_seconds = (
                        candidate_utc
                        - resolved_time
                    ).total_seconds()

                    return SessionWakeResult(
                        next_allowed_at=candidate_utc,
                        delay_seconds=delay_seconds,
                        reason=(
                            "The next allowed runtime session "
                            f"begins at "
                            f"{candidate.isoformat()}."
                        ),
                    )

        return SessionWakeResult(
            next_allowed_at=None,
            delay_seconds=None,
            reason=(
                "No allowed runtime session was found "
                "within the configured search window."
            ),
        )

    def _candidate_times(
        self,
        candidate_date: date,
    ) -> tuple[datetime, ...]:
        config = self.market_session_clock.config
        timezone_info = config.timezone

        if (
            candidate_date.weekday()
            not in config.weekdays
        ):
            return ()

        exchange_day = (
            self.market_session_clock
            .exchange_calendar
            .evaluate(
                candidate_date
            )
        )

        if exchange_day.is_holiday:
            return ()

        candidates: list[datetime] = []

        if self.session_policy.config.allow_premarket:
            candidates.append(
                self._combine(
                    candidate_date,
                    config.premarket_start,
                    timezone_info,
                )
            )

        if (
            self.session_policy
            .config
            .allow_regular_session
        ):
            candidates.append(
                self._combine(
                    candidate_date,
                    config.regular_start,
                    timezone_info,
                )
            )

        if (
            self.session_policy
            .config
            .allow_after_hours
        ):
            after_hours_start = (
                exchange_day.regular_close
                or config.regular_end
            )

            candidates.append(
                self._combine(
                    candidate_date,
                    after_hours_start,
                    timezone_info,
                )
            )

        return tuple(
            sorted(
                candidates
            )
        )

    @staticmethod
    def _combine(
        calendar_date: date,
        boundary_time: time,
        timezone_info,
    ) -> datetime:
        return datetime.combine(
            calendar_date,
            boundary_time,
            tzinfo=timezone_info,
        )

    @staticmethod
    def _resolve_time(
        value: datetime,
    ) -> datetime:
        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                "checked_at must be a datetime."
            )

        if value.tzinfo is None:
            raise ValueError(
                "checked_at must be timezone-aware."
            )

        return value.astimezone(
            timezone.utc
        )