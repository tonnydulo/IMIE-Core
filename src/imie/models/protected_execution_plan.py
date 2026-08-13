from __future__ import annotations

from dataclasses import dataclass

from imie.models.protected_order_slice import (
    ProtectedOrderSlice,
)


@dataclass(frozen=True, slots=True)
class ProtectedExecutionPlan:
    symbol: str
    side: str
    order_type: str
    entry_price: float | None
    time_in_force: str
    slices: tuple[ProtectedOrderSlice, ...]
    valid: bool
    actionable: bool
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
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
            self.slices,
            tuple,
        ) or not all(
            isinstance(
                item,
                ProtectedOrderSlice,
            )
            for item in self.slices
        ):
            raise TypeError(
                "slices must be a tuple of ProtectedOrderSlice."
            )

        if len(
            self.slices
        ) not in {
            1,
            2,
        }:
            raise ValueError(
                "slices must contain one or two protected orders."
            )

        labels = tuple(
            item.label
            for item in self.slices
        )

        if labels not in {
            ("target1",),
            ("target1", "target2"),
        }:
            raise ValueError(
                "slices must be ordered as target1, target2."
            )

        if len({
            item.stop_price
            for item in self.slices
        }) != 1:
            raise ValueError(
                "all slices must use the same stop price."
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

        if not isinstance(
            self.order_type,
            str,
        ):
            raise TypeError(
                "order_type must be a string."
            )

        order_type = self.order_type.strip().lower()

        if order_type not in {
            "market",
            "limit",
        }:
            raise ValueError(
                "order_type must be market or limit."
            )

        if (
            order_type == "limit"
            and self.entry_price is None
        ):
            raise ValueError(
                "a limit plan requires entry_price."
            )

        if (
            self.entry_price is not None
            and self.entry_price <= 0
        ):
            raise ValueError(
                "entry_price must be positive when provided."
            )

        if not isinstance(
            self.time_in_force,
            str,
        ):
            raise TypeError(
                "time_in_force must be a string."
            )

        time_in_force = self.time_in_force.strip().lower()

        if time_in_force not in {
            "day",
            "gtc",
        }:
            raise ValueError(
                "time_in_force must be day or gtc."
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

        warnings = tuple(
            warning.strip()
            for warning in self.warnings
            if isinstance(
                warning,
                str,
            )
            and warning.strip()
        )

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "order_type", order_type)
        object.__setattr__(self, "time_in_force", time_in_force)
        object.__setattr__(self, "warnings", warnings)

    @property
    def quantity(self) -> int:
        return sum(
            item.quantity
            for item in self.slices
        )
