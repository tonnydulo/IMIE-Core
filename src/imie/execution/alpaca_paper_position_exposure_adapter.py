from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from imie.models import BrokerPositionExposure


class AlpacaPositionExposureClient(Protocol):
    def get_all_positions(self) -> object:
        ...


class AlpacaPaperPositionExposureAdapter:
    """Translate read-only Alpaca paper position exposure into broker truth."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        trading_client: AlpacaPositionExposureClient,
        paper: bool,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if paper is not True:
            raise ValueError("position exposure queries are restricted to paper mode.")
        if not callable(getattr(trading_client, "get_all_positions", None)):
            raise TypeError("trading_client must expose get_all_positions().")
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._trading_client = trading_client
        self._clock = resolved_clock

    def get_open_position_exposure(self) -> BrokerPositionExposure:
        values = self._trading_client.get_all_positions()
        if not isinstance(values, list | tuple):
            raise TypeError("get_all_positions() must return a list or tuple.")

        symbols = tuple(
            self._symbol(getattr(position, "symbol", None))
            for position in values
        )
        observed_at = self._clock()
        if not isinstance(observed_at, datetime):
            raise TypeError("clock must return a datetime.")
        if observed_at.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        return BrokerPositionExposure(
            broker=self.broker_name,
            open_symbols=symbols,
            observed_at=observed_at,
        )

    @staticmethod
    def _symbol(value: object) -> str:
        if not isinstance(value, str):
            raise TypeError("Alpaca position symbol must be a string.")
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Alpaca position symbol cannot be empty.")
        return normalized
