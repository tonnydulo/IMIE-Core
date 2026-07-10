from dataclasses import dataclass, field


@dataclass(frozen=True)
class TradePlan:
    symbol: str
    strategy: str
    direction: str
    valid: bool
    actionable: bool
    decision: str

    entry: float | None
    stop: float | None
    target1: float | None
    target2: float | None

    risk_per_share: float | None
    reward1_per_share: float | None
    reward2_per_share: float | None
    rr1: float | None
    rr2: float | None

    quality: int
    confidence: float

    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    narrative: str = ""
