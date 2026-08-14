from datetime import datetime, timedelta, timezone

from imie.execution import (
    ProtectedExecutionPlanBuilder,
    ProtectedExecutionSafetyService,
)
from imie.models import (
    BrokerDailyPnlSnapshot,
    BrokerMarketSessionSnapshot,
    BrokerPositionExposure,
    ExecutionCandidate,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
    ProtectedOrderSubmission,
    ProtectedPlanSubmissionResult,
)


NOW = datetime(2026, 8, 14, 16, 0, tzinfo=timezone.utc)


def candidate():
    return ExecutionCandidate(
        symbol="NVDA", strategy="Pullback-to-Core", direction="long",
        quantity=10, entry=200, stop=199, target1=201, target2=202,
        position_notional=2_000, risk_amount=10, valid=True, actionable=True,
    )


def intent():
    return ExecutionOrderIntent(
        symbol="NVDA", side="buy", quantity=10, order_type="limit",
        entry_price=200, stop_price=199, target1_price=201,
        target2_price=202, time_in_force="day", valid=True, actionable=True,
    )


class Port:
    def __init__(self):
        self.calls = []

    def submit_protected_plan(self, plan):
        self.calls.append(plan)
        submissions = tuple(
            ProtectedOrderSubmission(
                label=item.label,
                quantity=item.quantity,
                accepted=True,
                broker_order_id=f"order-{item.label}",
                status="accepted",
                message="Accepted.",
            )
            for item in plan.slices
        )
        return ProtectedPlanSubmissionResult(
            broker="alpaca-paper", symbol=plan.symbol, side=plan.side,
            quantity=plan.quantity, accepted=True, status="accepted",
            message="Protected plan accepted.", submissions=submissions,
        )


class Reservations:
    def __init__(self):
        self.values = {}

    def reserve(self, value):
        if value.fingerprint in self.values:
            raise ValueError("already reserved")
        self.values[value.fingerprint] = value

    def get(self, fingerprint):
        return self.values.get(fingerprint)


class Exposure:
    def __init__(self, symbols, observed_at=NOW):
        self.symbols = symbols
        self.observed_at = observed_at

    def get_open_position_exposure(self):
        return BrokerPositionExposure(
            broker="alpaca-paper",
            open_symbols=tuple(self.symbols),
            observed_at=self.observed_at,
        )


class DailyPnl:
    def __init__(self, *, realized=0, unrealized=0, error=None):
        self.realized = realized
        self.unrealized = unrealized
        self.error = error
        self.calls = 0

    def get_daily_pnl(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return BrokerDailyPnlSnapshot(
            broker="alpaca-paper",
            realized_pnl=self.realized,
            unrealized_pnl=self.unrealized,
            observed_at=NOW,
        )


class MarketSession:
    def __init__(self, *, is_open=True, error=None):
        self.is_open = is_open
        self.error = error
        self.calls = 0

    def get_market_session(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return BrokerMarketSessionSnapshot(
            broker="alpaca-paper",
            is_open=self.is_open,
            observed_at=NOW,
        )


def service(port, reservations, **overrides):
    values = {
        "protected_execution_port": port,
        "policy": ExecutionSafetyPolicy(
            maximum_order_notional=5_000,
            maximum_risk_amount=25,
        ),
        "reservation_store": reservations,
        "clock": lambda: NOW,
    }
    values.update(overrides)
    return ProtectedExecutionSafetyService(**values)


def test_safe_plan_is_reserved_and_submitted_exactly_once():
    port = Port()
    reservations = Reservations()
    order_intent = intent()
    plan = ProtectedExecutionPlanBuilder().build(order_intent)

    result = service(port, reservations).submit(
        candidate=candidate(), intent=order_intent, plan=plan
    )

    assert result.submitted is True
    assert result.protected_submission.accepted is True
    assert result.reservation.symbol == "NVDA"
    assert port.calls == [plan]
    assert len(reservations.values) == 1


def test_kill_switch_blocks_before_reservation_and_submission():
    port = Port()
    reservations = Reservations()
    daily_pnl = DailyPnl(realized=-100)
    market_session = MarketSession()
    order_intent = intent()
    guarded = service(
        port,
        reservations,
        policy=ExecutionSafetyPolicy(
            maximum_order_notional=5_000,
            maximum_risk_amount=25,
            kill_switch_active=True,
        ),
        daily_pnl_port=daily_pnl,
        maximum_daily_loss=250,
        market_session_port=market_session,
    )

    result = guarded.submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is False
    assert result.assessment.kill_switch_active is True
    assert daily_pnl.calls == 0
    assert market_session.calls == 0
    assert reservations.values == {}
    assert port.calls == []


def test_daily_loss_below_limit_allows_protected_submission():
    port = Port()
    reservations = Reservations()
    daily_pnl = DailyPnl(realized=-100, unrealized=-25)
    order_intent = intent()

    result = service(
        port,
        reservations,
        daily_pnl_port=daily_pnl,
        maximum_daily_loss=250,
    ).submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is True
    assert result.daily_loss_assessment.allowed is True
    assert result.daily_loss_assessment.loss_amount == 125
    assert daily_pnl.calls == 1
    assert len(port.calls) == 1


def test_open_market_session_allows_protected_submission():
    port = Port()
    reservations = Reservations()
    market_session = MarketSession(is_open=True)
    order_intent = intent()

    result = service(
        port,
        reservations,
        market_session_port=market_session,
    ).submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is True
    assert result.market_session_assessment.allowed is True
    assert market_session.calls == 1
    assert len(port.calls) == 1


def test_closed_market_session_blocks_before_other_broker_queries():
    port = Port()
    reservations = Reservations()
    market_session = MarketSession(is_open=False)
    daily_pnl = DailyPnl(realized=-100)
    order_intent = intent()

    result = service(
        port,
        reservations,
        market_session_port=market_session,
        daily_pnl_port=daily_pnl,
        maximum_daily_loss=250,
    ).submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is False
    assert result.market_session_assessment.allowed is False
    assert market_session.calls == 1
    assert daily_pnl.calls == 0
    assert reservations.values == {}
    assert port.calls == []


def test_market_session_query_failure_stops_before_execution_mutation():
    port = Port()
    reservations = Reservations()
    market_session = MarketSession(error=RuntimeError("clock unavailable"))
    order_intent = intent()

    try:
        service(
            port,
            reservations,
            market_session_port=market_session,
        ).submit(
            candidate=candidate(),
            intent=order_intent,
            plan=ProtectedExecutionPlanBuilder().build(order_intent),
        )
    except RuntimeError as exc:
        assert "clock unavailable" in str(exc)
    else:
        raise AssertionError("market session query failure must propagate")

    assert reservations.values == {}
    assert port.calls == []


def test_market_session_port_must_satisfy_protocol():
    try:
        service(Port(), Reservations(), market_session_port=object())
    except TypeError as exc:
        assert "BrokerMarketSessionPort" in str(exc)
    else:
        raise AssertionError("invalid market session port must fail")


def test_daily_loss_at_limit_blocks_before_reservation_and_submission():
    port = Port()
    reservations = Reservations()
    daily_pnl = DailyPnl(realized=-200, unrealized=-50)
    order_intent = intent()

    result = service(
        port,
        reservations,
        daily_pnl_port=daily_pnl,
        maximum_daily_loss=250,
    ).submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is False
    assert result.daily_loss_assessment.allowed is False
    assert result.daily_loss_assessment.loss_amount == 250
    assert reservations.values == {}
    assert port.calls == []


def test_daily_pnl_query_failure_stops_before_execution_mutation():
    port = Port()
    reservations = Reservations()
    daily_pnl = DailyPnl(error=RuntimeError("broker unavailable"))
    order_intent = intent()

    try:
        service(
            port,
            reservations,
            daily_pnl_port=daily_pnl,
            maximum_daily_loss=250,
        ).submit(
            candidate=candidate(),
            intent=order_intent,
            plan=ProtectedExecutionPlanBuilder().build(order_intent),
        )
    except RuntimeError as exc:
        assert "broker unavailable" in str(exc)
    else:
        raise AssertionError("daily pnl query failure must propagate")

    assert reservations.values == {}
    assert port.calls == []


def test_daily_loss_configuration_must_be_complete():
    port = Port()
    reservations = Reservations()

    for overrides in (
        {"daily_pnl_port": DailyPnl()},
        {"maximum_daily_loss": 250},
    ):
        try:
            service(port, reservations, **overrides)
        except ValueError as exc:
            assert "configured together" in str(exc)
        else:
            raise AssertionError("partial daily loss configuration must fail")


def test_concurrent_limit_blocks_single_protected_submission():
    port = Port()
    reservations = Reservations()
    order_intent = intent()
    guarded = service(
        port,
        reservations,
        position_exposure_port=Exposure(("AAPL", "TSLA")),
        maximum_concurrent_positions=2,
    )

    result = guarded.submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is False
    assert result.concurrent_position_assessment.allowed is False
    assert reservations.values == {}
    assert port.calls == []


def test_stale_position_exposure_blocks_protected_submission():
    port = Port()
    reservations = Reservations()
    order_intent = intent()
    guarded = service(
        port,
        reservations,
        position_exposure_port=Exposure(
            ("AAPL",), observed_at=NOW - timedelta(seconds=5.001)
        ),
        maximum_concurrent_positions=2,
        maximum_position_exposure_age_seconds=5,
    )

    result = guarded.submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is False
    assert result.concurrent_position_assessment.exposure_fresh is False
    assert reservations.values == {}
    assert port.calls == []


def test_one_clock_value_authorizes_exposure_and_timestamps_reservation():
    calls = []

    def clock():
        calls.append(NOW)
        return NOW

    port = Port()
    reservations = Reservations()
    order_intent = intent()
    guarded = service(
        port,
        reservations,
        position_exposure_port=Exposure(("AAPL",)),
        maximum_concurrent_positions=2,
        maximum_position_exposure_age_seconds=5,
        clock=clock,
    )

    result = guarded.submit(
        candidate=candidate(),
        intent=order_intent,
        plan=ProtectedExecutionPlanBuilder().build(order_intent),
    )

    assert result.submitted is True
    assert result.reservation.reserved_at == NOW
    assert calls == [NOW]


def test_duplicate_reservation_stops_before_protected_port():
    port = Port()
    reservations = Reservations()
    guarded = service(port, reservations)
    order_intent = intent()
    plan = ProtectedExecutionPlanBuilder().build(order_intent)
    guarded.submit(candidate=candidate(), intent=order_intent, plan=plan)

    try:
        guarded.submit(candidate=candidate(), intent=order_intent, plan=plan)
    except ValueError as exc:
        assert "already reserved" in str(exc)
    else:
        raise AssertionError("duplicate reservation must fail")

    assert port.calls == [plan]


def test_mismatched_candidate_and_intent_fail_before_safety_mutation():
    port = Port()
    reservations = Reservations()
    order_intent = intent()
    mismatched = ExecutionCandidate(
        symbol="NVDA", strategy="Pullback-to-Core", direction="short",
        quantity=10, entry=200, stop=199, target1=201, target2=202,
        position_notional=2_000, risk_amount=10, valid=True, actionable=True,
    )

    try:
        service(port, reservations).submit(
            candidate=mismatched,
            intent=order_intent,
            plan=ProtectedExecutionPlanBuilder().build(order_intent),
        )
    except ValueError as exc:
        assert "direction" in str(exc)
    else:
        raise AssertionError("mismatched direction must fail")

    assert reservations.values == {}
    assert port.calls == []
