from __future__ import annotations

from dataclasses import dataclass

from imie.models.acceptance_result import AcceptanceResult
from imie.models.analyst_result import AnalystResult
from imie.models.institutional_bias import InstitutionalBias
from imie.models.institutional_confluence import (
    InstitutionalConfluence,
)
from imie.models.market_phase import MarketPhase
from imie.models.setup_lifecycle import SetupLifecycle
from imie.models.trade_plan import TradePlan


@dataclass(frozen=True, slots=True)
class InstitutionalDecisionContext:
    """
    Immutable orchestration context consumed by DecisionDirector v2.

    Combines institutional reasoning outputs with execution-layer
    analyses immediately before trade authorization.
    """

    institutional_bias: InstitutionalBias

    institutional_confluence: InstitutionalConfluence

    market_phase: MarketPhase

    trend: AnalystResult

    setup_lifecycle: SetupLifecycle

    acceptance: AcceptanceResult

    risk: TradePlan