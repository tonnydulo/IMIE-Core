from dataclasses import dataclass


@dataclass(frozen=True)
class SetupLifecycle:
    symbol: str
    state: str
    direction: str
    confidence: float
    atr_distance: float | None
    action: str
    reason: str
