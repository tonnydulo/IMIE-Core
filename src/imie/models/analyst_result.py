from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AnalystResult:
    """
    Standard contract implemented by every IMIE analyst.

    Every analyst reports:

    • who produced the opinion
    • whether the analyst is enabled
    • its opinion
    • confidence
    • supporting evidence
    • warnings
    • an optional analyst-specific payload

    Examples of payloads:

        TrendResult
        SetupLifecycle
        AcceptanceResult
        TradePlan
        StructureResult
        LiquidityResult
    """

    analyst: str
    opinion: str
    confidence: float

    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    payload: Any | None = None

    analyst_id: str = ""
    enabled: bool = True

    def __post_init__(self) -> None:
        analyst = self.analyst.strip()
        opinion = self.opinion.strip()

        if not analyst:
            raise ValueError(
                "Analyst name cannot be empty."
            )

        if not opinion:
            raise ValueError(
                "Analyst opinion cannot be empty."
            )

        analyst_id = (
            self.analyst_id.strip().upper()
            if self.analyst_id
            else analyst.upper()
            .replace("ANALYST", "")
            .replace("ENGINE", "")
            .replace(" ", "_")
            .strip("_")
        )

        confidence = max(
            0.0,
            min(100.0, float(self.confidence)),
        )

        object.__setattr__(
            self,
            "analyst",
            analyst,
        )

        object.__setattr__(
            self,
            "analyst_id",
            analyst_id,
        )

        object.__setattr__(
            self,
            "opinion",
            opinion,
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "evidence",
            self._clean_items(self.evidence),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(self.warnings),
        )

    @staticmethod
    def _clean_items(
        items: list[str],
    ) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(item).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return cleaned