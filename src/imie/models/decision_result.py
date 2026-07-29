from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from imie.models.institutional_decision_context import (
        InstitutionalDecisionContext,
    )
    from imie.models.trade_plan import TradePlan


class DirectorDecision(StrEnum):
    """
    Standardized recommendations produced by the Decision Director.

    Only the Decision Director may produce a final system-level
    recommendation.
    """

    IGNORE = "IGNORE"
    WAIT = "WAIT"
    PREPARE = "PREPARE"
    READY = "READY"
    PASS = "PASS"


@dataclass(frozen=True, slots=True)
class DecisionResult:
    """
    Final explainable recommendation produced by the Decision Director.

    The Decision Director may attach an existing TradePlan, but it must
    never modify that plan.

    analyst_summary stores the opinion and confidence reported by each
    contributing analyst.
    """

    decision: DirectorDecision
    actionable: bool
    confidence: float
    recommendation: str

    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    trade_plan: TradePlan | None = None

    institutional_context: InstitutionalDecisionContext | None = None

    analyst_summary: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        bounded_confidence = max(
            0.0,
            min(100.0, float(self.confidence)),
        )

        object.__setattr__(
            self,
            "confidence",
            bounded_confidence,
        )

        object.__setattr__(
            self,
            "recommendation",
            self.recommendation.strip(),
        )

        object.__setattr__(
            self,
            "reasons",
            self._clean_items(self.reasons),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(self.warnings),
        )

        object.__setattr__(
            self,
            "analyst_summary",
            self._freeze_summary(self.analyst_summary),
        )

        if not self.recommendation:
            raise ValueError(
                "Decision recommendation cannot be empty."
            )

        if (
            self.actionable
            and self.decision is not DirectorDecision.READY
        ):
            raise ValueError(
                "Only a READY decision may be actionable."
            )

        if (
            self.decision is DirectorDecision.READY
            and not self.actionable
        ):
            raise ValueError(
                "A READY decision must be actionable."
            )

        if (
            self.decision is DirectorDecision.READY
            and self.trade_plan is None
        ):
            raise ValueError(
                "A READY decision must include a TradePlan."
            )

        if (
            self.actionable
            and self.trade_plan is not None
            and not self.trade_plan.actionable
        ):
            raise ValueError(
                "An actionable decision cannot attach a "
                "non-actionable TradePlan."
            )

    @property
    def valid(self) -> bool:
        """
        A DecisionResult is valid when it satisfies its model invariants.

        WAIT, PREPARE, IGNORE, and PASS are valid system states even
        though they do not authorize execution.
        """

        return True

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

            seen.add(key)
            cleaned.append(text)

        return tuple(cleaned)

    @staticmethod
    def _freeze_summary(
        summary: Mapping[str, Mapping[str, Any]],
    ) -> Mapping[str, Mapping[str, Any]]:
        frozen_summary: dict[str, Mapping[str, Any]] = {}

        for analyst_id, details in summary.items():
            normalized_id = str(analyst_id).strip().upper()

            if not normalized_id:
                continue

            opinion = str(
                details.get("opinion", "")
            ).strip()

            raw_confidence = details.get(
                "confidence"
            )

            confidence_available = (
                "confidence" in details
                and raw_confidence is not None
            )

            confidence = max(
                0.0,
                min(
                    100.0,
                    float(
                        raw_confidence
                        if confidence_available
                        else 0.0
                    ),
                ),
            )

            enabled = bool(
                details.get("enabled", True)
            )

            frozen_summary[normalized_id] = MappingProxyType(
                {
                    "opinion": opinion,
                    "confidence": confidence,
                    "confidence_available": (
                        confidence_available
                    ),
                    "enabled": enabled,
                }
            )

        return MappingProxyType(frozen_summary)
    
    