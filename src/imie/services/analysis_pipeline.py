from __future__ import annotations

from dataclasses import replace

from imie.engines.risk.risk_analyst import (
    RiskAnalyst,
)
from imie.engines.setup.setup_lifecycle_engine import (
    SetupLifecycleEngine,
)
from imie.engines.trend.trend_analyst import (
    TrendAnalyst,
)

from imie.directors import (
    DecisionDirector,
)
from imie.engines.acceptance import (
    AcceptanceAnalyst,
)

from imie.models import (
    AcceptanceResult,
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    DecisionResult,
    SetupLifecycle,
    TradePlan,
    TradingContext,
)
from imie.services.institutional_pipeline import (
    build_institutional_results,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_TREND,
)


class AnalysisPipeline:
    """
    Executes all analysts and the DecisionDirector for one
    already-built TradingContext.

    Market-data acquisition, completed-bar validation, and context
    construction remain outside this service.
    """

    def __init__(
        self,
        *,
        trend_analyst: TrendAnalyst | None = None,
        lifecycle_engine: SetupLifecycleEngine | None = None,
        acceptance_analyst: AcceptanceAnalyst | None = None,
        risk_analyst: RiskAnalyst | None = None,
        decision_director: DecisionDirector | None = None,
    ) -> None:
        self.trend_analyst = (
            trend_analyst
            or TrendAnalyst()
        )

        self.lifecycle_engine = (
            lifecycle_engine
            or SetupLifecycleEngine()
        )

        self.acceptance_analyst = (
            acceptance_analyst
            or AcceptanceAnalyst()
        )

        self.risk_analyst = (
            risk_analyst
            or RiskAnalyst(
                minimum_rr=2.0,
                target1_r=1.0,
                target2_r=2.0,
            )
        )

        self.decision_director = (
            decision_director
            or DecisionDirector()
        )

    def evaluate(
        self,
        *,
        context: TradingContext,
        freshness: DataFreshness,
    ) -> DecisionResult:
        if not isinstance(
            context,
            TradingContext,
        ):
            raise TypeError(
                "context must be a TradingContext."
            )

        if not isinstance(
            freshness,
            DataFreshness,
        ):
            raise TypeError(
                "freshness must be a DataFreshness."
            )

        trend_result = self._build_trend_result(
            context
        )

        (
            structure_result,
            liquidity_result,
            order_block_result,
            auction_result,
            pressure_result,
            participation_result,
            value_result,
        ) = build_institutional_results(
            context,
            trend_result,
        )

        initial_lifecycle = (
            self.lifecycle_engine
            .evaluate_pullback_to_core(
                context,
                trend_result,
            )
        )

        acceptance_result = (
            self.acceptance_analyst
            .analyze_result(
                context,
                initial_lifecycle,
            )
        )

        acceptance_result = replace(
            acceptance_result,
            analyst_id=ANALYST_ACCEPTANCE,
        )

        acceptance = acceptance_result.payload

        if not isinstance(
            acceptance,
            AcceptanceResult,
        ):
            raise TypeError(
                "AcceptanceAnalyst did not produce an "
                "AcceptanceResult payload."
            )

        setup_result = self.lifecycle_engine.analyze(
            context,
            trend_result,
            acceptance_confirmed=acceptance.accepted,
        )

        setup_result = replace(
            setup_result,
            analyst_id=ANALYST_SETUP,
        )

        lifecycle = setup_result.payload

        if not isinstance(
            lifecycle,
            SetupLifecycle,
        ):
            raise TypeError(
                "SetupLifecycleEngine did not produce a "
                "SetupLifecycle payload."
            )

        risk_result = self.risk_analyst.analyze_result(
            context=context,
            freshness=freshness,
            trend_result=trend_result,
            lifecycle=lifecycle,
            acceptance=acceptance,
        )

        risk_result = replace(
            risk_result,
            analyst_id=ANALYST_RISK,
        )

        trade_plan = risk_result.payload

        if not isinstance(
            trade_plan,
            TradePlan,
        ):
            raise TypeError(
                "RiskAnalyst did not produce a TradePlan payload."
            )

        registry = AnalystRegistry()

        for result in (
            trend_result,
            structure_result,
            liquidity_result,
            order_block_result,
            auction_result,
            pressure_result,
            participation_result,
            value_result,
            setup_result,
            acceptance_result,
            risk_result,
        ):
            registry.register(
                result
            )

        return self.decision_director.evaluate(
            context=context,
            freshness=freshness,
            registry=registry,
        )

    def _build_trend_result(
        self,
        context: TradingContext,
    ) -> AnalystResult:
        result = self.trend_analyst.analyze(
            context
        )

        if not isinstance(
            result,
            AnalystResult,
        ):
            raise TypeError(
                "TrendAnalyst did not produce an AnalystResult."
            )

        return replace(
            result,
            analyst_id=ANALYST_TREND,
        )