from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProtectedOrderSlice:
    label: str
    quantity: int
    stop_price: float
    target_price: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.label,
            str,
        ):
            raise TypeError(
                "label must be a string."
            )

        label = self.label.strip().lower()

        if label not in {
            "target1",
            "target2",
        }:
            raise ValueError(
                "label must be target1 or target2."
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

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero."
            )

        for field_name in (
            "stop_price",
            "target_price",
        ):
            value = getattr(
                self,
                field_name,
            )

            if isinstance(
                value,
                bool,
            ) or not isinstance(
                value,
                int | float,
            ):
                raise TypeError(
                    f"{field_name} must be a number."
                )

            if value <= 0:
                raise ValueError(
                    f"{field_name} must be positive."
                )

            object.__setattr__(
                self,
                field_name,
                float(value),
            )

        object.__setattr__(
            self,
            "label",
            label,
        )
