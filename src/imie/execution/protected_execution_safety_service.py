from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Callable

from imie.execution.broker_position_exposure_port import (
    BrokerPositionExposurePort,
)
from imie.execution.broker_daily_pnl_port import BrokerDailyPnlPort
from imie.execution.daily_loss_safety_engine import DailyLossSafetyEngine
from imie.execution.broker_market_session_port import BrokerMarketSessionPort
from imie.execution.market_session_safety_engine import MarketSessionSafetyEngine
from imie.execution.concurrent_position_safety_engine import (
    ConcurrentPositionSafetyEngine,
)
from imie.execution.execution_safety_engine import ExecutionSafetyEngine
from imie.execution.execution_data_freshness_engine import (
    ExecutionDataFreshnessEngine,
)
from imie.execution.execution_submission_fingerprint import (
    ExecutionSubmissionFingerprint,
)
from imie.execution.execution_submission_reservation_store import (
    ExecutionSubmissionReservationStore,
)
from imie.execution.protected_execution_port import ProtectedExecutionPort
from imie.execution.protected_execution_plan_builder import (
    ProtectedExecutionPlanBuilder,
)
from imie.models import (
    ExecutionCandidate,
    DataFreshness,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
    ExecutionSubmissionReservation,
    ProtectedExecutionPlan,
    ProtectedExecutionSafetyResult,
    ProtectedPlanSubmissionResult,
)


class ProtectedExecutionSafetyService:
    """Authorize and forward exactly one protected plan submission."""

    def __init__(
        self,
        *,
        protected_execution_port: ProtectedExecutionPort,
        policy: ExecutionSafetyPolicy,
        reservation_store: ExecutionSubmissionReservationStore,
        position_exposure_port: BrokerPositionExposurePort | None = None,
        maximum_concurrent_positions: int | None = None,
        maximum_position_exposure_age_seconds: float | None = None,
        daily_pnl_port: BrokerDailyPnlPort | None = None,
        maximum_daily_loss: float | None = None,
        market_session_port: BrokerMarketSessionPort | None = None,
        maximum_market_session_age_seconds: float | None = None,
        require_data_freshness: bool = False,
        safety_engine: ExecutionSafetyEngine | None = None,
        data_freshness_engine: ExecutionDataFreshnessEngine | None = None,
        concurrent_engine: ConcurrentPositionSafetyEngine | None = None,
        daily_loss_engine: DailyLossSafetyEngine | None = None,
        market_session_engine: MarketSessionSafetyEngine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(protected_execution_port, ProtectedExecutionPort):
            raise TypeError(
                "protected_execution_port must satisfy ProtectedExecutionPort."
            )
        if not isinstance(policy, ExecutionSafetyPolicy):
            raise TypeError("policy must be an ExecutionSafetyPolicy.")
        if not isinstance(reservation_store, ExecutionSubmissionReservationStore):
            raise TypeError(
                "reservation_store must satisfy "
                "ExecutionSubmissionReservationStore."
            )
        if (position_exposure_port is None) != (
            maximum_concurrent_positions is None
        ):
            raise ValueError(
                "position_exposure_port and maximum_concurrent_positions "
                "must be configured together."
            )
        if position_exposure_port is not None and not isinstance(
            position_exposure_port, BrokerPositionExposurePort
        ):
            raise TypeError(
                "position_exposure_port must satisfy BrokerPositionExposurePort."
            )
        if maximum_concurrent_positions is not None and (
            isinstance(maximum_concurrent_positions, bool)
            or not isinstance(maximum_concurrent_positions, int)
            or maximum_concurrent_positions <= 0
        ):
            raise ValueError("maximum_concurrent_positions must be positive.")
        if (
            maximum_position_exposure_age_seconds is not None
            and maximum_concurrent_positions is None
        ):
            raise ValueError(
                "maximum_position_exposure_age_seconds requires "
                "maximum_concurrent_positions."
            )
        if maximum_position_exposure_age_seconds is not None and (
            isinstance(maximum_position_exposure_age_seconds, bool)
            or not isinstance(
                maximum_position_exposure_age_seconds, int | float
            )
            or maximum_position_exposure_age_seconds <= 0
        ):
            raise ValueError(
                "maximum_position_exposure_age_seconds must be positive."
            )
        if (daily_pnl_port is None) != (maximum_daily_loss is None):
            raise ValueError(
                "daily_pnl_port and maximum_daily_loss must be configured together."
            )
        if daily_pnl_port is not None and not isinstance(
            daily_pnl_port, BrokerDailyPnlPort
        ):
            raise TypeError("daily_pnl_port must satisfy BrokerDailyPnlPort.")
        if maximum_daily_loss is not None and (
            isinstance(maximum_daily_loss, bool)
            or not isinstance(maximum_daily_loss, int | float)
            or maximum_daily_loss <= 0
        ):
            raise ValueError("maximum_daily_loss must be positive.")
        if market_session_port is not None and not isinstance(
            market_session_port, BrokerMarketSessionPort
        ):
            raise TypeError(
                "market_session_port must satisfy BrokerMarketSessionPort."
            )
        if (
            maximum_market_session_age_seconds is not None
            and market_session_port is None
        ):
            raise ValueError(
                "maximum_market_session_age_seconds requires "
                "market_session_port."
            )
        if maximum_market_session_age_seconds is not None and (
            isinstance(maximum_market_session_age_seconds, bool)
            or not isinstance(maximum_market_session_age_seconds, int | float)
            or not math.isfinite(maximum_market_session_age_seconds)
            or maximum_market_session_age_seconds <= 0
        ):
            raise ValueError(
                "maximum_market_session_age_seconds must be finite and positive."
            )
        if not isinstance(require_data_freshness, bool):
            raise TypeError("require_data_freshness must be a bool.")
        self._protected_execution_port = protected_execution_port
        self._policy = policy
        self._reservation_store = reservation_store
        self._position_exposure_port = position_exposure_port
        self._maximum_concurrent_positions = maximum_concurrent_positions
        self._maximum_position_exposure_age_seconds = (
            float(maximum_position_exposure_age_seconds)
            if maximum_position_exposure_age_seconds is not None
            else None
        )
        self._daily_pnl_port = daily_pnl_port
        self._maximum_daily_loss = (
            float(maximum_daily_loss) if maximum_daily_loss is not None else None
        )
        self._market_session_port = market_session_port
        self._maximum_market_session_age_seconds = (
            float(maximum_market_session_age_seconds)
            if maximum_market_session_age_seconds is not None
            else None
        )
        self._safety_engine = safety_engine or ExecutionSafetyEngine()
        self._require_data_freshness = require_data_freshness
        self._data_freshness_engine = (
            data_freshness_engine or ExecutionDataFreshnessEngine()
        )
        self._concurrent_engine = concurrent_engine or ConcurrentPositionSafetyEngine()
        self._daily_loss_engine = daily_loss_engine or DailyLossSafetyEngine()
        self._market_session_engine = (
            market_session_engine or MarketSessionSafetyEngine()
        )
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def submit(
        self,
        *,
        candidate: ExecutionCandidate,
        intent: ExecutionOrderIntent,
        plan: ProtectedExecutionPlan,
        freshness: DataFreshness | None = None,
    ) -> ProtectedExecutionSafetyResult:
        self._validate_inputs(candidate=candidate, intent=intent, plan=plan)
        assessment = self._safety_engine.assess(
            candidate=candidate,
            policy=self._policy,
        )
        if not assessment.allowed:
            return ProtectedExecutionSafetyResult(
                assessment=assessment,
                protected_submission=None,
            )

        data_freshness_assessment = None
        if self._require_data_freshness:
            if freshness is None:
                raise ValueError(
                    "freshness is required when execution data freshness is enabled."
                )
            data_freshness_assessment = self._data_freshness_engine.assess(
                freshness
            )
            if not data_freshness_assessment.allowed:
                return ProtectedExecutionSafetyResult(
                    assessment=assessment,
                    data_freshness_assessment=data_freshness_assessment,
                    protected_submission=None,
                )

        checked_at = self._clock()
        if not isinstance(checked_at, datetime):
            raise TypeError("clock must return a datetime.")
        if checked_at.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")

        market_session_assessment = None
        if self._market_session_port is not None:
            market_session_snapshot = (
                self._market_session_port.get_market_session()
            )
            market_session_assessment = self._market_session_engine.assess(
                market_session_snapshot,
                checked_at=(
                    checked_at
                    if self._maximum_market_session_age_seconds is not None
                    else None
                ),
                maximum_session_age_seconds=(
                    self._maximum_market_session_age_seconds
                ),
            )
            if not market_session_assessment.allowed:
                return ProtectedExecutionSafetyResult(
                    assessment=assessment,
                    data_freshness_assessment=data_freshness_assessment,
                    market_session_assessment=market_session_assessment,
                    protected_submission=None,
                )

        daily_loss_assessment = None
        if self._daily_pnl_port is not None:
            daily_loss_snapshot = self._daily_pnl_port.get_daily_pnl()
            daily_loss_assessment = self._daily_loss_engine.assess(
                snapshot=daily_loss_snapshot,
                maximum_daily_loss=self._maximum_daily_loss,
            )
            if not daily_loss_assessment.allowed:
                return ProtectedExecutionSafetyResult(
                    assessment=assessment,
                    data_freshness_assessment=data_freshness_assessment,
                    market_session_assessment=market_session_assessment,
                    daily_loss_assessment=daily_loss_assessment,
                    protected_submission=None,
                )

        concurrent_assessment = None
        if self._position_exposure_port is not None:
            exposure = self._position_exposure_port.get_open_position_exposure()
            concurrent_assessment = self._concurrent_engine.assess(
                symbol=plan.symbol,
                exposure=exposure,
                maximum_concurrent_positions=self._maximum_concurrent_positions,
                checked_at=(
                    checked_at
                    if self._maximum_position_exposure_age_seconds is not None
                    else None
                ),
                maximum_exposure_age_seconds=(
                    self._maximum_position_exposure_age_seconds
                ),
            )
            if not concurrent_assessment.allowed:
                return ProtectedExecutionSafetyResult(
                    assessment=assessment,
                    data_freshness_assessment=data_freshness_assessment,
                    market_session_assessment=market_session_assessment,
                    concurrent_position_assessment=concurrent_assessment,
                    daily_loss_assessment=daily_loss_assessment,
                    protected_submission=None,
                )

        reservation = ExecutionSubmissionReservation(
            fingerprint=ExecutionSubmissionFingerprint.create(
                candidate=candidate,
                intent=intent,
            ),
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            reserved_at=checked_at,
        )
        self._reservation_store.reserve(reservation)
        submission = self._protected_execution_port.submit_protected_plan(plan)
        if not isinstance(submission, ProtectedPlanSubmissionResult):
            raise TypeError(
                "submit_protected_plan() must return "
                "ProtectedPlanSubmissionResult."
            )
        if (
            submission.symbol != plan.symbol
            or submission.side != plan.side
            or submission.quantity != plan.quantity
        ):
            raise ValueError("Protected submission identity does not match plan.")
        return ProtectedExecutionSafetyResult(
            assessment=assessment,
            data_freshness_assessment=data_freshness_assessment,
            market_session_assessment=market_session_assessment,
            concurrent_position_assessment=concurrent_assessment,
            daily_loss_assessment=daily_loss_assessment,
            reservation=reservation,
            protected_submission=submission,
        )

    @staticmethod
    def _validate_inputs(*, candidate, intent, plan) -> None:
        if not isinstance(candidate, ExecutionCandidate):
            raise TypeError("candidate must be an ExecutionCandidate.")
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        if not isinstance(plan, ProtectedExecutionPlan):
            raise TypeError("plan must be a ProtectedExecutionPlan.")
        if not (candidate.symbol == intent.symbol == plan.symbol):
            raise ValueError("candidate, intent, and plan symbols must match.")
        if not (candidate.quantity == intent.quantity == plan.quantity):
            raise ValueError("candidate, intent, and plan quantities must match.")
        if intent.side != plan.side:
            raise ValueError("intent and protected plan sides must match.")
        expected_side = "buy" if candidate.direction == "long" else "sell"
        if intent.side != expected_side:
            raise ValueError("candidate direction and intent side must match.")
        if plan != ProtectedExecutionPlanBuilder().build(intent):
            raise ValueError("protected plan must match the order intent.")
        for name, candidate_value, intent_value in (
            ("stop", candidate.stop, intent.stop_price),
            ("target1", candidate.target1, intent.target1_price),
            ("target2", candidate.target2, intent.target2_price),
        ):
            if not math.isclose(
                candidate_value,
                intent_value,
                rel_tol=1e-9,
                abs_tol=1e-6,
            ):
                raise ValueError(f"candidate and intent {name} must match.")
        if intent.order_type == "limit" and (
            intent.entry_price is None
            or not math.isclose(
                candidate.entry,
                intent.entry_price,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            raise ValueError("candidate and intent entry must match.")
        if candidate.valid != intent.valid or intent.valid != plan.valid:
            raise ValueError("candidate, intent, and plan validity must match.")
        if (
            candidate.actionable != intent.actionable
            or intent.actionable != plan.actionable
        ):
            raise ValueError(
                "candidate, intent, and plan actionability must match."
            )
