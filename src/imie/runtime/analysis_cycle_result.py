from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models import (
    DataFreshness,
    DecisionResult,
    MarketSnapshot,
    TradingContext,
)
from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)
from imie.runtime.completed_bar_result import (
    CompletedBarResult,
)
from imie.runtime.market_session_result import (
    MarketSessionResult,
)
from imie.runtime.session_policy_result import (
    SessionPolicyResult,
)


@dataclass(frozen=True, slots=True)
class AnalysisCycleResult:
    """
    Result of one IMIE runtime analysis cycle.

    A cycle can complete successfully, be skipped because no new
    completed bar exists, stop because market data is stale, or fail
    because an operational exception occurred.
    """

    status: AnalysisCycleStatus
    symbol: str
    timeframe: str
    started_at: datetime
    completed_at: datetime

    message: str

    market_session: MarketSessionResult | None = None
    session_policy: SessionPolicyResult | None = None
    completed_bar: CompletedBarResult | None = None
    snapshot: MarketSnapshot | None = None
    freshness: DataFreshness | None = None
    context: TradingContext | None = None
    decision: DecisionResult | None = None

    error_type: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.status,
            AnalysisCycleStatus,
        ):
            raise TypeError(
                "status must be an AnalysisCycleStatus."
            )

        symbol = self._normalize_required_text(
            self.symbol,
            "symbol",
        ).upper()

        timeframe = self._normalize_required_text(
            self.timeframe,
            "timeframe",
        ).lower()

        message = self._normalize_required_text(
            self.message,
            "message",
        )

        if not isinstance(
            self.started_at,
            datetime,
        ):
            raise TypeError(
                "started_at must be a datetime."
            )

        if not isinstance(
            self.completed_at,
            datetime,
        ):
            raise TypeError(
                "completed_at must be a datetime."
            )

        if self.started_at.tzinfo is None:
            raise ValueError(
                "started_at must be timezone-aware."
            )

        if self.completed_at.tzinfo is None:
            raise ValueError(
                "completed_at must be timezone-aware."
            )

        if self.completed_at < self.started_at:
            raise ValueError(
                "completed_at cannot be earlier than started_at."
            )

        if (
            self.completed_bar is not None
            and not isinstance(
                self.completed_bar,
                CompletedBarResult,
            )
        ):
            raise TypeError(
                "completed_bar must be a CompletedBarResult "
                "or None."
            )

        if (
            self.snapshot is not None
            and not isinstance(
                self.snapshot,
                MarketSnapshot,
            )
        ):
            raise TypeError(
                "snapshot must be a MarketSnapshot or None."
            )

        if (
            self.freshness is not None
            and not isinstance(
                self.freshness,
                DataFreshness,
            )
        ):
            raise TypeError(
                "freshness must be a DataFreshness or None."
            )

        if (
            self.context is not None
            and not isinstance(
                self.context,
                TradingContext,
            )
        ):
            raise TypeError(
                "context must be a TradingContext or None."
            )

        if (
            self.decision is not None
            and not isinstance(
                self.decision,
                DecisionResult,
            )
        ):
            raise TypeError(
                "decision must be a DecisionResult or None."
            )

        error_type = self.error_type

        if error_type is not None:
            error_type = str(
                error_type
            ).strip() or None

        if (
            self.status is AnalysisCycleStatus.COMPLETED
            and self.decision is None
        ):
            raise ValueError(
                "A completed cycle must contain a decision."
            )

        if (
            self.status is AnalysisCycleStatus.STALE_DATA
            and self.freshness is None
        ):
            raise ValueError(
                "A stale-data cycle must contain freshness."
            )

        if (
            self.status is AnalysisCycleStatus.FAILED
            and error_type is None
        ):
            raise ValueError(
                "A failed cycle must contain error_type."
            )
        
        if (
            self.market_session is not None
            and not isinstance(
                self.market_session,
                MarketSessionResult,
            )
        ):
            raise TypeError(
                "market_session must be a MarketSessionResult "
                "or None."
            )

        if (
            self.session_policy is not None
            and not isinstance(
                self.session_policy,
                SessionPolicyResult,
            )
        ):
            raise TypeError(
                "session_policy must be a SessionPolicyResult "
                "or None."
            )

        if (
            self.status
            is AnalysisCycleStatus.SKIPPED_SESSION
            and self.session_policy is None
        ):
            raise ValueError(
                "A session-skipped cycle must contain "
                "session_policy."
            )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )

        object.__setattr__(
            self,
            "timeframe",
            timeframe,
        )

        object.__setattr__(
            self,
            "message",
            message,
        )

        object.__setattr__(
            self,
            "error_type",
            error_type,
        )

    @property
    def succeeded(self) -> bool:
        return self.status is AnalysisCycleStatus.COMPLETED

    @property
    def skipped(self) -> bool:
        return self.status in {
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR,
            AnalysisCycleStatus.SKIPPED_SESSION,
        }

    @property
    def failed(self) -> bool:
        return self.status is AnalysisCycleStatus.FAILED

    @staticmethod
    def _normalize_required_text(
        value: object,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{name} cannot be empty."
            )

        return normalized