from __future__ import annotations

import math

from datetime import datetime, timezone
from typing import Callable, Protocol

from imie.models import BrokerDailyPnlSnapshot


class AlpacaDailyPnlClient(Protocol):
    def get_account(self) -> object:
        ...

    def get_all_positions(self) -> object:
        ...


class AlpacaPaperDailyPnlAdapter:
    """Translate read-only Alpaca paper account truth into daily P&L."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        trading_client: AlpacaDailyPnlClient,
        paper: bool,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if paper is not True:
            raise ValueError("daily P&L queries are restricted to paper mode.")
        for method_name in ("get_account", "get_all_positions"):
            if not callable(getattr(trading_client, method_name, None)):
                raise TypeError(
                    f"trading_client must expose {method_name}()."
                )
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._trading_client = trading_client
        self._clock = resolved_clock

    def get_daily_pnl(self) -> BrokerDailyPnlSnapshot:
        account = self._trading_client.get_account()
        equity = self._number(getattr(account, "equity", None), "equity")
        last_equity = self._number(
            getattr(account, "last_equity", None), "last_equity"
        )
        positions = self._trading_client.get_all_positions()
        if not isinstance(positions, list | tuple):
            raise TypeError("get_all_positions() must return a list or tuple.")
        unrealized_pnl = sum(
            self._number(
                getattr(position, "unrealized_intraday_pl", None),
                "unrealized_intraday_pl",
            )
            for position in positions
        )
        total_pnl = equity - last_equity
        realized_pnl = total_pnl - unrealized_pnl
        observed_at = self._clock()
        if not isinstance(observed_at, datetime):
            raise TypeError("clock must return a datetime.")
        if observed_at.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        return BrokerDailyPnlSnapshot(
            broker=self.broker_name,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            observed_at=observed_at,
        )

    @staticmethod
    def _number(value: object, name: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Alpaca {name} must be numeric.") from exc
        if not math.isfinite(number):
            raise ValueError(f"Alpaca {name} must be finite.")
        return number
