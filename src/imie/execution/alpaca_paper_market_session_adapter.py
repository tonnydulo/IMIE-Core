from __future__ import annotations

from datetime import datetime
from typing import Protocol

from imie.models import BrokerMarketSessionSnapshot


class AlpacaMarketSessionClient(Protocol):
    def get_clock(self) -> object:
        ...


class AlpacaPaperMarketSessionAdapter:
    """Translate the read-only Alpaca paper clock into session truth."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        trading_client: AlpacaMarketSessionClient,
        paper: bool,
    ) -> None:
        if paper is not True:
            raise ValueError("market-session queries are restricted to paper mode.")
        if not callable(getattr(trading_client, "get_clock", None)):
            raise TypeError("trading_client must expose get_clock().")
        self._trading_client = trading_client

    def get_market_session(self) -> BrokerMarketSessionSnapshot:
        clock = self._trading_client.get_clock()
        is_open = getattr(clock, "is_open", None)
        if not isinstance(is_open, bool):
            raise TypeError("Alpaca clock is_open must be a bool.")
        return BrokerMarketSessionSnapshot(
            broker=self.broker_name,
            is_open=is_open,
            observed_at=self._aware_datetime(
                getattr(clock, "timestamp", None), "timestamp"
            ),
            next_open=self._aware_datetime(
                getattr(clock, "next_open", None), "next_open"
            ),
            next_close=self._aware_datetime(
                getattr(clock, "next_close", None), "next_close"
            ),
        )

    @staticmethod
    def _aware_datetime(value: object, name: str) -> datetime:
        if not isinstance(value, datetime):
            raise TypeError(f"Alpaca clock {name} must be a datetime.")
        if value.tzinfo is None:
            raise ValueError(
                f"Alpaca clock {name} must be timezone-aware."
            )
        return value
