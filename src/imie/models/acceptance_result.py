from dataclasses import dataclass, field


@dataclass(frozen=True)
class AcceptanceResult:
    symbol: str
    accepted: bool
    direction: str
    level: str
    score: int
    confidence: float
    trigger_price: float | None
    previous_level: float | None
    pullback_low: float | None
    pullback_high: float | None
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reason: str = ""
