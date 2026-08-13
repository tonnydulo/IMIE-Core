from __future__ import annotations

from datetime import UTC, datetime

from imie.execution import (
    BrokerExecutionPort,
    ProtectedExecutionPlanBuilder,
    ProtectedExecutionPort,
)

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
from imie.engines.position_sizing import (
    PositionSizingEngine,
)
from imie.runtime.position_sizing_config import (
    PositionSizingConfig,
)
from imie.engines.execution import (
    ExecutionCandidateBuilder,
    ExecutionOrderIntentBuilder,
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
    print, or persist. Broker submission occurs only when an
    execution port is explicitly provided.
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
        position_sizing_engine: PositionSizingEngine | None = None,
        position_sizing_config: PositionSizingConfig | None = None,
        execution_candidate_builder: ExecutionCandidateBuilder | None = None,
        execution_order_intent_builder: ExecutionOrderIntentBuilder | None = None,
        broker_execution_port: BrokerExecutionPort | None = None,
        protected_execution_port: ProtectedExecutionPort | None = None,
        protected_execution_plan_builder: (
            ProtectedExecutionPlanBuilder | None
        ) = None,
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

        self.position_sizing_engine = (
            position_sizing_engine
            or PositionSizingEngine()
        )

        self.position_sizing_config = (
            position_sizing_config
            or PositionSizingConfig()
        )

        self.execution_candidate_builder = (
            execution_candidate_builder
            or ExecutionCandidateBuilder()
        )

        self.execution_order_intent_builder = (
            execution_order_intent_builder
            or ExecutionOrderIntentBuilder()
        )

        self.broker_execution_port = broker_execution_port
        self.protected_execution_port = protected_execution_port
        self.protected_execution_plan_builder = (
            protected_execution_plan_builder
            or ProtectedExecutionPlanBuilder()
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

        if not isinstance(
            self.position_sizing_engine,
            PositionSizingEngine,
        ):
            raise TypeError(
                "position_sizing_engine must be a "
                "PositionSizingEngine."
            )

        if not isinstance(
            self.position_sizing_config,
            PositionSizingConfig,
        ):
            raise TypeError(
                "position_sizing_config must be a "
                "PositionSizingConfig."
            )

        if not isinstance(
            self.execution_candidate_builder,
            ExecutionCandidateBuilder,
        ):
            raise TypeError(
                "execution_candidate_builder must be an "
                "ExecutionCandidateBuilder."
            )

        if not isinstance(
            self.execution_order_intent_builder,
            ExecutionOrderIntentBuilder,
        ):
            raise TypeError(
                "execution_order_intent_builder must be an "
                "ExecutionOrderIntentBuilder."
            )

        if (
            self.broker_execution_port is not None
            and not callable(
                getattr(
                    self.broker_execution_port,
                    "submit_order",
                    None,
                )
            )

        ):
            raise TypeError(
                "broker_execution_port must provide submit_order()."
            )

        if (
            self.protected_execution_port is not None
            and not callable(
                getattr(
                    self.protected_execution_port,
                    "submit_protected_plan",
                    None,
                )
            )
        ):
            raise TypeError(
                "protected_execution_port must provide "
                "submit_protected_plan()."
            )

        if (
            self.broker_execution_port is not None
            and self.protected_execution_port is not None
        ):
            raise ValueError(
                "Only one broker execution port may be configured."
            )

        if not isinstance(
            self.protected_execution_plan_builder,
            ProtectedExecutionPlanBuilder,
        ):
            raise TypeError(
                "protected_execution_plan_builder must be a "
                "ProtectedExecutionPlanBuilder."
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

            position_size = None
            execution_candidate = None
            execution_order_intent = None
            broker_submission_result = None
            protected_submission_result = None

            if (
                self.position_sizing_config.enabled
                and decision.actionable
                and decision.trade_plan is not None
                and decision.trade_plan.actionable
            ):
                account_equity = (
                    self.position_sizing_config.account_equity
                )

                if account_equity is None:
                    raise RuntimeError(
                        "Position sizing is enabled without "
                        "account equity."
                    )

                position_size = (
                    self.position_sizing_engine.calculate(
                        decision.trade_plan,
                        account_equity=account_equity,
                        risk_percent=(
                            self.position_sizing_config.risk_percent
                        ),
                        buying_power=(
                            self.position_sizing_config.buying_power
                        ),
                        maximum_notional=(
                            self.position_sizing_config.maximum_notional
                        ),
                    )
                )

            if position_size is not None:
                execution_candidate = (
                    self.execution_candidate_builder.build(
                        decision=decision,
                        position_size=position_size,
                    )
                )

            if execution_candidate is not None:
                execution_order_intent = (
                    self.execution_order_intent_builder.build(
                        candidate=execution_candidate,
                    )
                )

            if (
                execution_order_intent is not None
                and execution_order_intent.valid
                and execution_order_intent.actionable
                and self.broker_execution_port is not None
            ):
                broker_submission_result = (
                    self.broker_execution_port.submit_order(
                        execution_order_intent
                    )
                )

            if (
                execution_order_intent is not None
                and execution_order_intent.valid
                and execution_order_intent.actionable
                and self.protected_execution_port is not None
            ):
                protected_plan = (
                    self.protected_execution_plan_builder.build(
                        execution_order_intent
                    )
                )
                protected_submission_result = (
                    self.protected_execution_port.submit_protected_plan(
                        protected_plan
                    )
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
                position_size=position_size,
                execution_candidate=execution_candidate,
                execution_order_intent=execution_order_intent,
                broker_submission_result=broker_submission_result,
                protected_submission_result=protected_submission_result,
            )

        except (
            OSError,
            RuntimeError,
            TimeoutError,
            ValueError,
        ) as exc:
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
                UTC
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
            UTC
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(
            UTC
        )
