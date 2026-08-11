from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PositionSizingConfig:
    enabled: bool = False

    account_equity: float | None = None
    risk_percent: float = 0.50

    buying_power: float | None = None
    maximum_notional: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.enabled,
            bool,
        ):
            raise TypeError(
                "enabled must be a bool."
            )

        risk_percent = self._positive_float(
            self.risk_percent,
            "risk_percent",
        )

        account_equity = self._optional_positive_float(
            self.account_equity,
            "account_equity",
        )

        buying_power = self._optional_positive_float(
            self.buying_power,
            "buying_power",
        )

        maximum_notional = self._optional_positive_float(
            self.maximum_notional,
            "maximum_notional",
        )

        if (
            self.enabled
            and account_equity is None
        ):
            raise ValueError(
                "account_equity is required when "
                "position sizing is enabled."
            )

        object.__setattr__(
            self,
            "risk_percent",
            risk_percent,
        )

        object.__setattr__(
            self,
            "account_equity",
            account_equity,
        )

        object.__setattr__(
            self,
            "buying_power",
            buying_power,
        )

        object.__setattr__(
            self,
            "maximum_notional",
            maximum_notional,
        )

    @staticmethod
    def _positive_float(
        value: object,
        name: str,
    ) -> float:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be numeric."
            )

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
                f"{name} must be greater than zero."
            )

        return normalized

    @classmethod
    def _optional_positive_float(
        cls,
        value: object,
        name: str,
    ) -> float | None:
        if value is None:
            return None

        return cls._positive_float(
            value,
            name,
        )