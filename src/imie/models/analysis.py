from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Analysis:
    symbol: str
    timestamp: datetime
    bias: str = "neutral"
    confidence: float = 0.0
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    recommendation: str = "wait"

    def add_reason(self, reason: str) -> None:
        self.reasons.append(reason)
