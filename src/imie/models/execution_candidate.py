from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionCandidate:
    symbol: str
    strategy: str
    direction: str
    quantity: int
    entry: float
    stop: float
    target1: float
    target2: float
    position_notional: float
    risk_amount: float
    valid: bool
    actionable: bool
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        symbol = self.symbol.upper().strip()
        strategy = self.strategy.strip()
        direction = self.direction.lower().strip()

        if not symbol:
            raise ValueError(
                "symbol must not be empty."
            )

        if not strategy:
            raise ValueError(
                "strategy must not be empty."
            )

        if direction not in {
            "long",
            "short",
        }:
            raise ValueError(
                "direction must be 'long' or 'short'."
            )

        if self.quantity < 0:
            raise ValueError(
                "quantity must not be negative."
            )

        if self.entry <= 0:
            raise ValueError(
                "entry must be greater than zero."
            )

        if self.stop <= 0:
            raise ValueError(
                "stop must be greater than zero."
            )

        if self.target1 <= 0:
            raise ValueError(
                "target1 must be greater than zero."
            )

        if self.target2 <= 0:
            raise ValueError(
                "target2 must be greater than zero."
            )

        if self.position_notional < 0:
            raise ValueError(
                "position_notional must not be negative."
            )

        if self.risk_amount < 0:
            raise ValueError(
                "risk_amount must not be negative."
            )

        if not isinstance(
            self.valid,
            bool,
        ):
            raise TypeError(
                "valid must be a bool."
            )

        if not isinstance(
            self.actionable,
            bool,
        ):
            raise TypeError(
                "actionable must be a bool."
            )

        if self.actionable and self.quantity <= 0:
            raise ValueError(
                "actionable execution candidate must "
                "have a positive quantity."
            )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "strategy",
            strategy,
        )
        object.__setattr__(
            self,
            "direction",
            direction,
        )
        object.__setattr__(
            self,
            "reasons",
            tuple(
                reason.strip()
                for reason in self.reasons
                if reason.strip()
            ),
        )
        object.__setattr__(
            self,
            "warnings",
            tuple(
                warning.strip()
                for warning in self.warnings
                if warning.strip()
            ),
        )