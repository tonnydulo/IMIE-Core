from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionOrderIntent:
    symbol: str
    side: str
    quantity: int
    order_type: str
    entry_price: float | None
    stop_price: float
    target1_price: float
    target2_price: float
    time_in_force: str
    valid: bool
    actionable: bool
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(
        self,
    ) -> None:
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

        object.__setattr__(
            self,
            "symbol",
            symbol,
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
                "side must be 'buy' or 'sell'."
            )

        object.__setattr__(
            self,
            "side",
            side,
        )

        if (
            not isinstance(
                self.quantity,
                int,
            )
            or isinstance(
                self.quantity,
                bool,
            )
        ):
            raise TypeError(
                "quantity must be an integer."
            )

        if self.quantity < 0:
            raise ValueError(
                "quantity cannot be negative."
            )

        if not isinstance(
            self.order_type,
            str,
        ):
            raise TypeError(
                "order_type must be a string."
            )

        order_type = (
            self.order_type
            .strip()
            .lower()
        )

        if order_type not in {
            "market",
            "limit",
        }:
            raise ValueError(
                "order_type must be "
                "'market' or 'limit'."
            )

        object.__setattr__(
            self,
            "order_type",
            order_type,
        )

        if (
            self.entry_price is not None
            and self.entry_price <= 0
        ):
            raise ValueError(
                "entry_price must be positive "
                "when provided."
            )

        for field_name in (
            "stop_price",
            "target1_price",
            "target2_price",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value <= 0:
                raise ValueError(
                    f"{field_name} must be positive."
                )

        if not isinstance(
            self.time_in_force,
            str,
        ):
            raise TypeError(
                "time_in_force must be a string."
            )

        time_in_force = (
            self.time_in_force
            .strip()
            .lower()
        )

        if time_in_force not in {
            "day",
            "gtc",
        }:
            raise ValueError(
                "time_in_force must be "
                "'day' or 'gtc'."
            )

        object.__setattr__(
            self,
            "time_in_force",
            time_in_force,
        )

        for field_name in (
            "valid",
            "actionable",
        ):
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                bool,
            ):
                raise TypeError(
                    f"{field_name} must be a bool."
                )

        if (
            self.actionable
            and self.quantity <= 0
        ):
            raise ValueError(
                "An actionable order intent "
                "must have positive quantity."
            )

        reasons = tuple(
            reason.strip()
            for reason in self.reasons
            if reason.strip()
        )

        warnings = tuple(
            warning.strip()
            for warning in self.warnings
            if warning.strip()
        )

        object.__setattr__(
            self,
            "reasons",
            reasons,
        )

        object.__setattr__(
            self,
            "warnings",
            warnings,
        )