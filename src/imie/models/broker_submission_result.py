from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokerSubmissionResult:
    broker: str
    symbol: str
    side: str
    quantity: int
    accepted: bool
    broker_order_id: str | None
    status: str
    message: str
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.broker,
            str,
        ):
            raise TypeError(
                "broker must be a string."
            )

        broker = self.broker.strip().lower()

        if not broker:
            raise ValueError(
                "broker cannot be empty."
            )

        if not isinstance(
            self.symbol,
            str,
        ):
            raise TypeError(
                "symbol must be a string."
            )

        symbol = self.symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "symbol cannot be empty."
            )

        if not isinstance(
            self.side,
            str,
        ):
            raise TypeError(
                "side must be a string."
            )

        side = self.side.strip().lower()

        if side not in {
            "buy",
            "sell",
        }:
            raise ValueError(
                "side must be buy or sell."
            )

        if isinstance(
            self.quantity,
            bool,
        ) or not isinstance(
            self.quantity,
            int,
        ):
            raise TypeError(
                "quantity must be an int."
            )

        if self.quantity < 0:
            raise ValueError(
                "quantity cannot be negative."
            )

        if not isinstance(
            self.accepted,
            bool,
        ):
            raise TypeError(
                "accepted must be a bool."
            )

        if (
            self.broker_order_id
            is not None
            and not isinstance(
                self.broker_order_id,
                str,
            )
        ):
            raise TypeError(
                "broker_order_id must be a string or None."
            )

        broker_order_id = (
            self.broker_order_id.strip()
            if self.broker_order_id
            is not None
            else None
        )

        if broker_order_id == "":
            broker_order_id = None

        if not isinstance(
            self.status,
            str,
        ):
            raise TypeError(
                "status must be a string."
            )

        status = self.status.strip().lower()

        if not status:
            raise ValueError(
                "status cannot be empty."
            )

        if not isinstance(
            self.message,
            str,
        ):
            raise TypeError(
                "message must be a string."
            )

        message = self.message.strip()

        if not message:
            raise ValueError(
                "message cannot be empty."
            )

        warnings = tuple(
            warning.strip()
            for warning in self.warnings
            if isinstance(
                warning,
                str,
            )
            and warning.strip()
        )

        object.__setattr__(
            self,
            "broker",
            broker,
        )
        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "side",
            side,
        )
        object.__setattr__(
            self,
            "broker_order_id",
            broker_order_id,
        )
        object.__setattr__(
            self,
            "status",
            status,
        )
        object.__setattr__(
            self,
            "message",
            message,
        )
        object.__setattr__(
            self,
            "warnings",
            warnings,
        )