from __future__ import annotations

from datetime import datetime, time, timezone

from imie.runtime.exchange_calendar import (
    ExchangeCalendar,
)
from imie.runtime.market_session_config import (
    MarketSessionConfig,
)
from imie.runtime.market_session_result import (
    MarketSessionResult,
)
from imie.runtime.market_session_state import (
    MarketSessionState,
)


class MarketSessionClock:
    """
    Classifies a timezone-aware timestamp into a U.S. equity
    market session.

    Weekday, holiday, normal-close, and early-close behavior are
    determined using MarketSessionConfig and ExchangeCalendar.
    """

    def __init__(
        self,
        config: MarketSessionConfig | None = None,
        exchange_calendar: ExchangeCalendar | None = None,
    ) -> None:
        self.config = (
            config
            or MarketSessionConfig()
        )

        self.exchange_calendar = (
            exchange_calendar
            or ExchangeCalendar()
        )

        if not isinstance(
            self.config,
            MarketSessionConfig,
        ):
            raise TypeError(
                "config must be a MarketSessionConfig."
            )

        if not isinstance(
            self.exchange_calendar,
            ExchangeCalendar,
        ):
            raise TypeError(
                "exchange_calendar must be an "
                "ExchangeCalendar."
            )

    def evaluate(
        self,
        checked_at: datetime | None = None,
    ) -> MarketSessionResult:
        resolved_time = self._resolve_time(
            checked_at
        )

        market_time = resolved_time.astimezone(
            self.config.timezone
        )

        exchange_day = (
            self.exchange_calendar.evaluate(
                market_time.date()
            )
        )

        is_weekday = (
            market_time.weekday()
            in self.config.weekdays
        )

        if not is_weekday:
            return MarketSessionResult(
                state=MarketSessionState.CLOSED,
                checked_at=resolved_time,
                market_time=market_time,
                is_trading_day=False,
                exchange_day=exchange_day,
                reason=(
                    "The configured market is closed "
                    "because today is not a trading day."
                ),
            )

        if exchange_day.is_holiday:
            return MarketSessionResult(
                state=MarketSessionState.CLOSED,
                checked_at=resolved_time,
                market_time=market_time,
                is_trading_day=False,
                exchange_day=exchange_day,
                reason=(
                    "The configured market is closed for "
                    f"{exchange_day.holiday_name}."
                ),
            )

        regular_close = self._regular_close(
            exchange_day.regular_close
        )

        after_hours_close = self._after_hours_close(
            exchange_day.after_hours_close
        )

        current_time = market_time.time().replace(
            tzinfo=None
        )

        if (
            self.config.premarket_start
            <= current_time
            < self.config.regular_start
        ):
            return MarketSessionResult(
                state=MarketSessionState.PREMARKET,
                checked_at=resolved_time,
                market_time=market_time,
                is_trading_day=True,
                exchange_day=exchange_day,
                reason=(
                    "The market is in the premarket "
                    "session."
                ),
            )

        if (
            self.config.regular_start
            <= current_time
            < regular_close
        ):
            return MarketSessionResult(
                state=(
                    MarketSessionState
                    .REGULAR_SESSION
                ),
                checked_at=resolved_time,
                market_time=market_time,
                is_trading_day=True,
                exchange_day=exchange_day,
                reason=(
                    "The market is in the regular "
                    "trading session."
                ),
            )

        if (
            regular_close
            <= current_time
            < after_hours_close
        ):
            return MarketSessionResult(
                state=MarketSessionState.AFTER_HOURS,
                checked_at=resolved_time,
                market_time=market_time,
                is_trading_day=True,
                exchange_day=exchange_day,
                reason=(
                    "The market is in the after-hours "
                    "session."
                ),
            )

        return MarketSessionResult(
            state=MarketSessionState.CLOSED,
            checked_at=resolved_time,
            market_time=market_time,
            is_trading_day=True,
            exchange_day=exchange_day,
            reason=(
                "The market is outside configured "
                "trading-session hours."
            ),
        )

    def _regular_close(
        self,
        exchange_close: time | None,
    ) -> time:
        return (
            exchange_close
            or self.config.regular_end
        )

    def _after_hours_close(
        self,
        exchange_close: time | None,
    ) -> time:
        return (
            exchange_close
            or self.config.after_hours_end
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