from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import requests


class HttpResponse(Protocol):
    def raise_for_status(self) -> None:
        ...

    def json(self) -> object:
        ...


class HttpSession(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, object],
        timeout: float,
    ) -> HttpResponse:
        ...


@dataclass(frozen=True, slots=True)
class AlpacaFillActivity:
    id: str
    order_id: str
    symbol: str
    side: str
    qty: str
    price: str
    transaction_time: datetime


class AlpacaPaperFillActivitySource:
    """Read genuine fill activities from Alpaca's paper endpoint."""

    base_url = "https://paper-api.alpaca.markets"
    page_size = 100

    def __init__(
        self,
        *,
        api_key: str,
        secret_key: str,
        session: HttpSession | None = None,
        timeout_seconds: float = 10.0,
        maximum_pages: int = 100,
    ) -> None:
        self._api_key = self._credential(api_key, "api_key")
        self._secret_key = self._credential(secret_key, "secret_key")
        if isinstance(timeout_seconds, bool) or not isinstance(
            timeout_seconds,
            int | float,
        ):
            raise TypeError("timeout_seconds must be a number.")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
        if isinstance(maximum_pages, bool) or not isinstance(maximum_pages, int):
            raise TypeError("maximum_pages must be an int.")
        if maximum_pages <= 0:
            raise ValueError("maximum_pages must be greater than zero.")

        resolved_session = session or requests.Session()
        if not callable(getattr(resolved_session, "get", None)):
            raise TypeError("session must expose get().")
        self._session = resolved_session
        self._timeout_seconds = float(timeout_seconds)
        self._maximum_pages = maximum_pages

    def get_fill_activities(
        self,
        broker_order_id: str,
    ) -> tuple[AlpacaFillActivity, ...]:
        order_id = self._order_id(broker_order_id)
        activities: list[AlpacaFillActivity] = []
        page_token: str | None = None
        seen_tokens: set[str] = set()

        for _ in range(self._maximum_pages):
            params: dict[str, object] = {
                "order_id": order_id,
                "direction": "asc",
                "page_size": self.page_size,
            }
            if page_token is not None:
                params["page_token"] = page_token

            response = self._session.get(
                f"{self.base_url}/v2/account/activities/FILL",
                headers={
                    "APCA-API-KEY-ID": self._api_key,
                    "APCA-API-SECRET-KEY": self._secret_key,
                },
                params=params,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise TypeError("Alpaca fill activity response must be a list.")

            page = tuple(
                self._parse_activity(item, expected_order_id=order_id)
                for item in payload
            )
            activities.extend(page)

            if len(page) < self.page_size:
                return tuple(activities)
            next_token = page[-1].id
            if next_token in seen_tokens:
                raise RuntimeError("Alpaca fill activity pagination repeated a token.")
            seen_tokens.add(next_token)
            page_token = next_token

        raise RuntimeError("Alpaca fill activity pagination exceeded maximum_pages.")

    @staticmethod
    def _parse_activity(
        payload: object,
        *,
        expected_order_id: str,
    ) -> AlpacaFillActivity:
        if not isinstance(payload, dict):
            raise TypeError("Alpaca fill activity must be an object.")

        activity_type = str(
            payload.get("activity_type", payload.get("type", ""))
        ).strip().lower()
        if activity_type not in {"fill", "partial_fill"}:
            raise ValueError("Alpaca activity is not a fill activity.")

        order_id = str(payload.get("order_id", "")).strip()
        if order_id != expected_order_id:
            raise ValueError(
                "Alpaca fill activity order_id does not match the requested order."
            )

        transaction_time = payload.get("transaction_time")
        if not isinstance(transaction_time, str):
            raise TypeError("transaction_time must be an ISO-8601 string.")
        try:
            parsed_time = datetime.fromisoformat(
                transaction_time.strip().replace("Z", "+00:00")
            )
        except ValueError:
            raise ValueError("transaction_time must be valid ISO-8601.") from None
        if parsed_time.tzinfo is None:
            raise ValueError("transaction_time must be timezone-aware.")

        values = {
            name: str(payload.get(name, "")).strip()
            for name in ("id", "symbol", "side", "qty", "price")
        }
        for name, value in values.items():
            if not value:
                raise ValueError(f"Alpaca fill activity {name} cannot be empty.")

        return AlpacaFillActivity(
            id=values["id"],
            order_id=order_id,
            symbol=values["symbol"],
            side=values["side"],
            qty=values["qty"],
            price=values["price"],
            transaction_time=parsed_time,
        )

    @staticmethod
    def _credential(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{name} cannot be empty.")
        return normalized

    @staticmethod
    def _order_id(value: object) -> str:
        if not isinstance(value, str):
            raise TypeError("broker_order_id must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError("broker_order_id cannot be empty.")
        return normalized

