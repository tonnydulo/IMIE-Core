from __future__ import annotations

from datetime import datetime

from datetime import datetime, timezone

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)
from imie.runtime.single_analysis_cycle import (
    SingleAnalysisCycle,
)


class RuntimeRunner:
    """
    Runs one IMIE analysis cycle with provider lifecycle management.

    The runner connects before execution and always attempts to
    disconnect afterward, including when connection or execution fails.
    """

    def __init__(
        self,
        *,
        market_data: object,
        cycle: SingleAnalysisCycle,
    ) -> None:
        if not callable(
            getattr(
                market_data,
                "connect",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide connect()."
            )

        if not callable(
            getattr(
                market_data,
                "disconnect",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide disconnect()."
            )

        if not isinstance(
            cycle,
            SingleAnalysisCycle,
        ):
            raise TypeError(
                "cycle must be a SingleAnalysisCycle."
            )

        self.market_data = market_data
        self.cycle = cycle

    def run_once(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        connected = False

        try:
            self.market_data.connect()
            connected = True

            return self.cycle.run(
                checked_at=checked_at,
            )

        except Exception as exc:
            now = self._resolve_time(
                checked_at
            )

            return AnalysisCycleResult(
                status=AnalysisCycleStatus.FAILED,
                symbol=self.cycle.config.symbol,
                timeframe=self.cycle.config.timeframe,
                started_at=now,
                completed_at=now,
                message=(
                    str(exc)
                    or "Runtime runner failed."
                ),
                error_type=type(exc).__name__,
            )

        finally:
            if connected:
                try:
                    self.market_data.disconnect()
                except Exception:
                    pass

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