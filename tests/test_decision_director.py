from datetime import datetime, timezone
from imie.directors.decision_director import (
    DecisionDirector,
    DecisionDirectorConfig,
)
from imie.models import (
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    DecisionResult,
    TradePlan,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_TREND,
)
from imie.utils.constants import (
    LIFECYCLE_READY,
    TREND_BULLISH,
    TREND_NEUTRAL,
)


def create_director() -> DecisionDirector:
    return DecisionDirector(
        DecisionDirectorConfig(
            minimum_ready_confidence=60,
        )
    )


def create_registry() -> AnalystRegistry:
    return AnalystRegistry()


def create_freshness(
    *,
    actionable: bool = True,
    status: str = "FRESH",
    reason: str = "",
) -> DataFreshness:
    timestamp = datetime.now(timezone.utc)

    return DataFreshness(
        checked_at=timestamp,
        quote_timestamp=timestamp,
        latest_bar_timestamp=timestamp,
        quote_age_seconds=0.0,
        bar_age_seconds=0.0,
        quote_bar_gap_seconds=0.0,
        quote_is_fresh=actionable,
        bar_is_fresh=actionable,
        timestamps_aligned=actionable,
        actionable=actionable,
        status=status,
        reason=reason,
    )


def test_wait_when_required_analysts_missing():
    director = create_director()
    registry = create_registry()

    result = director.evaluate(
        context=None,
        freshness=create_freshness(),
        registry=registry,
    )

    assert isinstance(result, DecisionResult)
    assert result.decision.value == "WAIT"
    assert result.actionable is False

def test_ignore_when_trend_is_neutral():
    director = create_director()
    registry = create_registry()

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_NEUTRAL,
            confidence=80,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion=LIFECYCLE_READY,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="STRONG",
            confidence=90,
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": True},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="READY",
            confidence=90,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
    )

    assert result.decision.value == "IGNORE"

    assert result.actionable is False

def test_prepare_when_setup_is_returning_to_core():
    director = create_director()
    registry = create_registry()

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_BULLISH,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion="RETURNING_TO_CORE",
            confidence=85,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="NONE",
            confidence=0,
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": False},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="WAIT",
            confidence=0,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
    )

    assert result.decision.value == "PREPARE"
    assert result.actionable is False

def test_prepare_when_at_core_without_acceptance():
    director = create_director()
    registry = create_registry()

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_BULLISH,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion="AT_CORE",
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="NONE",
            confidence=0,
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": False},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="WAIT",
            confidence=0,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
    )

    assert result.decision.value == "PREPARE"
    assert result.actionable is False
    assert "acceptance" in result.recommendation.lower()

def test_pass_when_risk_analyst_has_no_trade_plan():
    director = create_director()
    registry = create_registry()

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_BULLISH,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion=LIFECYCLE_READY,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="STRONG",
            confidence=85,
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": True},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="READY",
            confidence=85,
            payload=None,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
)

    assert result.decision.value == "PASS"
    assert result.actionable is False
    assert result.trade_plan is None
    assert "tradeplan" in result.recommendation.lower()

def test_pass_when_trade_plan_is_invalid():
    director = create_director()
    registry = create_registry()

    invalid_plan = TradePlan(
        symbol="SPY",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        valid=False,
        actionable=False,
        decision="PASS",
        entry=None,
        stop=None,
        target1=None,
        target2=None,
        risk_per_share=None,
        reward1_per_share=None,
        reward2_per_share=None,
        rr1=None,
        rr2=None,
        quality=0,
        confidence=0.0,
        reasons=[],
        warnings=[
            "Projected reward-to-risk failed validation."
        ],
        narrative="The proposed TradePlan is invalid.",
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_BULLISH,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion=LIFECYCLE_READY,
            confidence=90,
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="STRONG",
            confidence=85,
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": True},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="PASS",
            confidence=0,
            payload=invalid_plan,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
)

    assert result.decision.value == "PASS"
    assert result.actionable is False
    assert result.trade_plan is invalid_plan
    assert "failed risk validation" in result.recommendation.lower()

def test_ready_when_all_required_conditions_are_satisfied():
    director = create_director()
    registry = create_registry()

    valid_plan = TradePlan(
        symbol="SPY",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        valid=True,
        actionable=True,
        decision="READY",
        entry=500.00,
        stop=499.00,
        target1=501.00,
        target2=502.00,
        risk_per_share=1.00,
        reward1_per_share=1.00,
        reward2_per_share=2.00,
        rr1=1.00,
        rr2=2.00,
        quality=90,
        confidence=90.0,
        reasons=[
            "Risk validation passed.",
            "Projected Target 2 provides 2.00R.",
        ],
        warnings=[],
        narrative="A valid Pullback-to-Core TradePlan is available.",
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            enabled=True,
            opinion=TREND_BULLISH,
            confidence=90,
            evidence=["Bullish trend confirmed."],
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            enabled=True,
            opinion=LIFECYCLE_READY,
            confidence=90,
            evidence=["Setup lifecycle is READY."],
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            enabled=True,
            opinion="STRONG",
            confidence=85,
            evidence=["Completed-candle acceptance confirmed."],
            payload=type(
                "AcceptancePayload",
                (),
                {"accepted": True},
            )(),
        )
    )

    registry.register(
        AnalystResult(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            enabled=True,
            opinion="READY",
            confidence=90,
            evidence=["Risk analysis produced an actionable TradePlan."],
            payload=valid_plan,
        )
    )

    result = director.evaluate(
    context=None,
    freshness=create_freshness(),
    registry=registry,
)

    assert result.decision.value == "READY"
    assert result.actionable is True
    assert result.trade_plan is valid_plan
    assert result.confidence >= 60
    assert result.analyst_summary["TREND"]["opinion"] == TREND_BULLISH
    assert "execute" in result.recommendation.lower()

def test_pass_when_market_data_is_stale():
    director = create_director()
    registry = create_registry()

    result = director.evaluate(
        context=None,
        freshness=create_freshness(
            actionable=False,
            status="STALE",
            reason="Latest quote is stale.",
        ),
        registry=registry,
    )

    assert result.decision.value == "PASS"
    assert result.actionable is False
    assert result.confidence == 0
    assert result.trade_plan is None
    assert "fresh" in result.recommendation.lower()