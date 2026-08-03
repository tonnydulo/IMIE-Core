from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """
    Configuration for one IMIE runtime analysis process.

    The runtime initially supports one symbol and deterministic
    completed-bar polling. Multi-symbol scheduling is introduced
    separately.
    """

    symbol: str = "NVDA"
    timeframe: str = "2m"
    bar_limit: int = 500

    polling_interval_seconds: float = 5.0
    closed_session_polling_interval_seconds: float = 300.0
    completion_delay_seconds: float = 3.0
    require_new_completed_bar: bool = True
    heartbeat_interval_seconds: float = 60.0

    def __post_init__(self) -> None:
        symbol = self._normalize_symbol(
            self.symbol
        )

        timeframe = self._normalize_timeframe(
            self.timeframe
        )

        bar_limit = self._normalize_positive_int(
            value=self.bar_limit,
            name="bar_limit",
        )

        polling_interval_seconds = (
            self._normalize_positive_float(
                value=self.polling_interval_seconds,
                name="polling_interval_seconds",
            )
        )

        completion_delay_seconds = (
            self._normalize_non_negative_float(
                value=self.completion_delay_seconds,
                name="completion_delay_seconds",
            )
        )

        if not isinstance(
            self.require_new_completed_bar,
            bool,
        ):
            raise TypeError(
                "require_new_completed_bar must be a bool."
            )

        if isinstance(
            self.closed_session_polling_interval_seconds,
            bool,
        ) or not isinstance(
            self.closed_session_polling_interval_seconds,
            int | float,
        ):
            raise TypeError(
                "closed_session_polling_interval_seconds "
                "must be a number."
            )
        
        if isinstance(
            self.heartbeat_interval_seconds,
            bool,
        ) or not isinstance(
            self.heartbeat_interval_seconds,
            int | float,
        ):
            raise TypeError(
                "heartbeat_interval_seconds must be a number."
            )

        if self.heartbeat_interval_seconds <= 0:
            raise ValueError(
                "heartbeat_interval_seconds must be greater than zero."
            )

        if (
            self.closed_session_polling_interval_seconds
            <= 0.0
        ):
            raise ValueError(
                "closed_session_polling_interval_seconds "
                "must be greater than zero."
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
            "bar_limit",
            bar_limit,
        )

        object.__setattr__(
            self,
            "polling_interval_seconds",
            polling_interval_seconds,
        )

        object.__setattr__(
            self,
            "completion_delay_seconds",
            completion_delay_seconds,
        )

        object.__setattr__(
            self,
            "closed_session_polling_interval_seconds",
            float(
                self.closed_session_polling_interval_seconds
            ),
        )

        object.__setattr__(
            self,
            "heartbeat_interval_seconds",
            float(
                self.heartbeat_interval_seconds
            ),
        )
       

    @staticmethod
    def _normalize_symbol(
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "symbol must be a string."
            )

        symbol = value.strip().upper()

        if not symbol:
            raise ValueError(
                "symbol cannot be empty."
            )

        return symbol

    @staticmethod
    def _normalize_timeframe(
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "timeframe must be a string."
            )

        timeframe = value.strip().lower()

        supported = {
            "1m",
            "2m",
            "5m",
            "15m",
        }

        if timeframe not in supported:
            raise ValueError(
                "timeframe must be one of: "
                "1m, 2m, 5m, or 15m."
            )

        return timeframe

    @staticmethod
    def _normalize_positive_int(
        *,
        value: object,
        name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be an int."
            )

        try:
            normalized = int(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be an int."
            ) from exc

        if normalized != value:
            raise TypeError(
                f"{name} must be an int."
            )

        if normalized < 1:
            raise ValueError(
                f"{name} must be at least 1."
            )

        return normalized

    @staticmethod
    def _normalize_positive_float(
        *,
        value: object,
        name: str,
    ) -> float:
        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be numeric."
            ) from exc

        if normalized <= 0.0:
            raise ValueError(
                f"{name} must be greater than 0."
            )

        return normalized

    @staticmethod
    def _normalize_non_negative_float(
        *,
        value: object,
        name: str,
    ) -> float:
        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be numeric."
            ) from exc

        if normalized < 0.0:
            raise ValueError(
                f"{name} cannot be negative."
            )

        return normalized

    @property
    def timeframe_minutes(self) -> int:
        return int(
            self.timeframe.removesuffix(
                "m"
            )
        )