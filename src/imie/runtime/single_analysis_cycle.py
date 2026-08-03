from __future__ import annotations

from datetime import datetime, timezone

from imie.models import MarketSnapshot
from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)
from imie.runtime.completed_bar_guard import (
    CompletedBarGuard,
)
from imie.runtime.market_session_clock import (
    MarketSessionClock,
)
from imie.runtime.runtime_config import (
    RuntimeConfig,
)
from imie.runtime.session_policy import (
    SessionPolicy,
)
from imie.services import (
    AnalysisPipeline,
    ContextBuilder,
    DataFreshnessGuard,
)


class SingleAnalysisCycle:
    """
    Executes one complete IMIE runtime cycle.

    The cycle:

    1. Evaluates the current market session.
    2. Applies the configured session policy.
    3. Fetches quote and bar data when analysis is allowed.
    4. Rejects incomplete or duplicate bars.
    5. Builds and validates a MarketSnapshot.
    6. Builds TradingContext.
    7. Runs the full analysis pipeline.
    8. Returns a typed AnalysisCycleResult.

    This class does not connect, disconnect, sleep, poll, retry,
    print, persist, or execute trades.
    """

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        market_data: object,
        completed_bar_guard: CompletedBarGuard | None = None,
        freshness_guard: DataFreshnessGuard | None = None,
        context_builder: ContextBuilder | None = None,
        analysis_pipeline: AnalysisPipeline | None = None,
        market_session_clock: MarketSessionClock | None = None,
        session_policy: SessionPolicy | None = None,
    ) -> None:
        if not isinstance(
            config,
            RuntimeConfig,
        ):
            raise TypeError(
                "config must be a RuntimeConfig."
            )

        if not callable(
            getattr(
                market_data,
                "get_quote",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide get_quote()."
            )

        if not callable(
            getattr(
                market_data,
                "get_bars",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide get_bars()."
            )

        self.config = config
        self.market_data = market_data

        self.completed_bar_guard = (
            completed_bar_guard
            or CompletedBarGuard(
                timeframe_minutes=(
                    config.timeframe_minutes
                ),
                completion_delay_seconds=(
                    config.completion_delay_seconds
                ),
            )
        )

        self.freshness_guard = (
            freshness_guard
            or DataFreshnessGuard()
        )

        self.context_builder = (
            context_builder
            or ContextBuilder(
                atr_tolerance=0.25,
            )
        )

        self.analysis_pipeline = (
            analysis_pipeline
            or AnalysisPipeline()
        )

        self.market_session_clock = (
            market_session_clock
            or MarketSessionClock()
        )

        self.session_policy = (
            session_policy
            or SessionPolicy()
        )

        if not isinstance(
            self.market_session_clock,
            MarketSessionClock,
        ):
            raise TypeError(
                "market_session_clock must be a "
                "MarketSessionClock."
            )

        if not isinstance(
            self.session_policy,
            SessionPolicy,
        ):
            raise TypeError(
                "session_policy must be a SessionPolicy."
            )

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        started_at = self._resolve_time(
            checked_at
        )

        market_session = (
            self.market_session_clock.evaluate(
                started_at
            )
        )

        session_policy_result = (
            self.session_policy.evaluate(
                market_session
            )
        )

        if session_policy_result.should_skip:
            return AnalysisCycleResult(
                status=(
                    AnalysisCycleStatus.SKIPPED_SESSION
                ),
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
                started_at=started_at,
                completed_at=self._now(),
                message=session_policy_result.reason,
                market_session=market_session,
                session_policy=session_policy_result,
            )

        try:
            quote = self.market_data.get_quote(
                self.config.symbol
            )

            bars = self.market_data.get_bars(
                self.config.symbol,
                self.config.timeframe,
                limit=self.config.bar_limit,
            )

            completed_bar = (
                self.completed_bar_guard.evaluate(
                    bars=bars,
                    checked_at=started_at,
                )
            )

            if (
                self.config.require_new_completed_bar
                and not completed_bar.accepted
            ):
                return AnalysisCycleResult(
                    status=(
                        AnalysisCycleStatus
                        .SKIPPED_NO_NEW_BAR
                    ),
                    symbol=self.config.symbol,
                    timeframe=self.config.timeframe,
                    started_at=started_at,
                    completed_at=self._now(),
                    message=completed_bar.reason,
                    market_session=market_session,
                    session_policy=session_policy_result,
                    completed_bar=completed_bar,
                )

            snapshot = MarketSnapshot(
                symbol=self.config.symbol,
                timestamp=quote.timestamp,
                quote=quote,
                bars=bars,
                timeframe=self.config.timeframe,
            )

            freshness = self.freshness_guard.evaluate(
                snapshot,
                checked_at=started_at,
            )

            if not freshness.actionable:
                return AnalysisCycleResult(
                    status=(
                        AnalysisCycleStatus.STALE_DATA
                    ),
                    symbol=self.config.symbol,
                    timeframe=self.config.timeframe,
                    started_at=started_at,
                    completed_at=self._now(),
                    message=freshness.reason,
                    market_session=market_session,
                    session_policy=session_policy_result,
                    completed_bar=completed_bar,
                    snapshot=snapshot,
                    freshness=freshness,
                )

            context = self.context_builder.build(
                snapshot
            )

            decision = self.analysis_pipeline.evaluate(
                context=context,
                freshness=freshness,
            )

            return AnalysisCycleResult(
                status=AnalysisCycleStatus.COMPLETED,
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
                started_at=started_at,
                completed_at=self._now(),
                message=(
                    "IMIE analysis cycle completed "
                    "successfully."
                ),
                market_session=market_session,
                session_policy=session_policy_result,
                completed_bar=completed_bar,
                snapshot=snapshot,
                freshness=freshness,
                context=context,
                decision=decision,
            )

        except Exception as exc:
            return AnalysisCycleResult(
                status=AnalysisCycleStatus.FAILED,
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
                started_at=started_at,
                completed_at=self._now(),
                message=(
                    str(exc)
                    or "Analysis cycle failed."
                ),
                market_session=market_session,
                session_policy=session_policy_result,
                error_type=type(exc).__name__,
            )

    @staticmethod
    def _resolve_time(
        value: datetime | None,
    ) -> datetime:
        if value is None:
            return datetime.now(
                timezone.utc
            )

        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                "checked_at must be a datetime or None."
            )

        if value.tzinfo is None:
            raise ValueError(
                "checked_at must be timezone-aware."
            )

        return value.astimezone(
            timezone.utc
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(
            timezone.utc
        )