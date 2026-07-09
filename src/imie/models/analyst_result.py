from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnalystResult:
    analyst: str
    opinion: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
