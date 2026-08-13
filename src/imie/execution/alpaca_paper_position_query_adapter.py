from __future__ import annotations

import math

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Callable, Protocol

from imie.models import BrokerPositionSnapshot, PositionDirection


class AlpacaPositionClient(Protocol):
    def get_open_position(self, symbol_or_asset_id: str) -> object:
        ...


class AlpacaPaperPositionQueryAdapter:
    """Translate fresh Alpaca paper position truth without broker mutation."""

    broker_name = "alpaca-paper"

    def __init__(
        self,
        *,
        trading_client: AlpacaPositionClient,
        paper: bool,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if paper is not True:
            raise ValueError("position queries are restricted to paper mode.")
        if not callable(getattr(trading_client, "get_open_position", None)):
            raise TypeError("trading_client must expose get_open_position().")
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._trading_client = trading_client
        self._clock = resolved_clock

    def get_position(self, symbol: str) -> BrokerPositionSnapshot | None:
        normalized_symbol = self._symbol(symbol)
        try:
            value = self._trading_client.get_open_position(normalized_symbol)
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                return None
            raise

        returned_symbol = self._symbol(getattr(value, "symbol", ""))
        if returned_symbol != normalized_symbol:
            raise ValueError("Alpaca position symbol does not match request.")
        side = self._enum_value(getattr(value, "side", ""))
        if side not in {"long", "short"}:
            raise ValueError("Alpaca position side must be long or short.")
        quantity = self._whole_quantity(getattr(value, "qty", None))
        observed_at = self._clock()
        if not isinstance(observed_at, datetime):
            raise TypeError("clock must return a datetime.")
        return BrokerPositionSnapshot(
            broker=self.broker_name,
            symbol=returned_symbol,
            direction=PositionDirection(side),
            quantity=quantity,
            average_entry_price=self._number(
                getattr(value, "avg_entry_price", None),
                "avg_entry_price",
                positive=True,
            ),
            market_price=self._optional_number(
                getattr(value, "current_price", None), "current_price"
            ),
            unrealized_pnl=self._number(
                getattr(value, "unrealized_pl", 0), "unrealized_pl"
            ),
            observed_at=observed_at,
        )

    @staticmethod
    def _symbol(value: object) -> str:
        if not isinstance(value, str):
            raise TypeError("symbol must be a string.")
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("symbol cannot be empty.")
        return normalized

    @staticmethod
    def _whole_quantity(value: object) -> int:
        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("Alpaca position qty must be numeric.") from exc
        quantity = abs(quantity)
        if quantity <= 0 or quantity != quantity.to_integral_value():
            raise ValueError("Alpaca position qty must be positive whole shares.")
        return int(quantity)

    @classmethod
    def _optional_number(cls, value: object, name: str) -> float | None:
        if value is None or str(value).strip() == "":
            return None
        return cls._number(value, name, positive=True)

    @staticmethod
    def _number(value: object, name: str, *, positive: bool = False) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Alpaca position {name} must be numeric.") from exc
        if not math.isfinite(number):
            raise ValueError(f"Alpaca position {name} must be finite.")
        if positive and number <= 0:
            raise ValueError(f"Alpaca position {name} must be positive.")
        return number

    @staticmethod
    def _enum_value(value: object) -> str:
        return str(getattr(value, "value", value)).strip().lower()
