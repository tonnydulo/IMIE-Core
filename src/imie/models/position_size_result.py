from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PositionSizeResult:
    symbol: str
    direction: str

    account_equity: float
    risk_percent: float
    risk_budget: float

    entry: float
    stop: float
    risk_per_share: float

    quantity: int
    position_notional: float

    actual_risk: float
    actual_risk_percent: float

    valid: bool
    actionable: bool

    reasons: tuple[str, ...] = field(
        default_factory=tuple
    )
    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        direction = self.direction.strip().lower()

        if not symbol:
            raise ValueError(
                "PositionSizeResult symbol cannot be empty."
            )

        if direction not in {
            "long",
            "short",
        }:
            raise ValueError(
                "PositionSizeResult direction must be "
                "long or short."
            )

        if self.account_equity <= 0:
            raise ValueError(
                "account_equity must be greater than zero."
            )

        if self.risk_percent <= 0:
            raise ValueError(
                "risk_percent must be greater than zero."
            )

        if self.risk_budget < 0:
            raise ValueError(
                "risk_budget cannot be negative."
            )

        if self.entry <= 0:
            raise ValueError(
                "entry must be greater than zero."
            )

        if self.stop <= 0:
            raise ValueError(
                "stop must be greater than zero."
            )

        if self.risk_per_share <= 0:
            raise ValueError(
                "risk_per_share must be greater than zero."
            )

        if self.quantity < 0:
            raise ValueError(
                "quantity cannot be negative."
            )

        if self.position_notional < 0:
            raise ValueError(
                "position_notional cannot be negative."
            )

        if self.actual_risk < 0:
            raise ValueError(
                "actual_risk cannot be negative."
            )

        if self.actual_risk_percent < 0:
            raise ValueError(
                "actual_risk_percent cannot be negative."
            )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        object.__setattr__(
            self,
            "reasons",
            self._clean_items(
                self.reasons
            ),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(
                self.warnings
            ),
        )

    @staticmethod
    def _clean_items(
        items: tuple[str, ...],
    ) -> tuple[str, ...]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(item).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(
                key
            )

            cleaned.append(
                text
            )

        return tuple(
            cleaned
        )