from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.runtime.market_session_state import (
    MarketSessionState,
)
from imie.runtime.exchange_calendar_day import (
    ExchangeCalendarDay,
)


@dataclass(frozen=True, slots=True)
class MarketSessionResult:
    state: MarketSessionState
    checked_at: datetime
    market_time: datetime
    is_trading_day: bool
    reason: str
    exchange_day: ExchangeCalendarDay | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.state,
            MarketSessionState,
        ):
            raise TypeError(
                "state must be a MarketSessionState."
            )

        for name in (
            "checked_at",
            "market_time",
        ):
            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                datetime,
            ):
                raise TypeError(
                    f"{name} must be a datetime."
                )

            if value.tzinfo is None:
                raise ValueError(
                    f"{name} must be timezone-aware."
                )

        if not isinstance(
            self.is_trading_day,
            bool,
        ):
            raise TypeError(
                "is_trading_day must be a bool."
            )

        reason = str(
            self.reason
        ).strip()

        if not reason:
            raise ValueError(
                "reason cannot be empty."
            )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

        if (
            self.exchange_day is not None
            and not isinstance(
                self.exchange_day,
                ExchangeCalendarDay,
            )
        ):
            raise TypeError(
                "exchange_day must be an "
                "ExchangeCalendarDay or None."
            )

    @property
    def is_open_session(self) -> bool:
        return self.state in {
            MarketSessionState.PREMARKET,
            MarketSessionState.REGULAR_SESSION,
            MarketSessionState.AFTER_HOURS,
        }

    @property
    def is_regular_session(self) -> bool:
        return (
            self.state
            is MarketSessionState.REGULAR_SESSION
        )
    
    @property
    def is_exchange_holiday(self) -> bool:
        return (
            self.exchange_day is not None
            and self.exchange_day.is_holiday
        )

    @property
    def is_early_close(self) -> bool:
        return (
            self.exchange_day is not None
            and self.exchange_day.is_early_close
        )
    