from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionState:
    symbol: str
    direction: str
    state: str
    core_type: str
    core_price: float | None
    distance_to_core: float | None
    atr: float | None
    tolerance: float | None
    reason: str
