from datetime import datetime, timedelta, timezone

import pytest

from imie.models import (
    DataFreshness,
    DecisionResult,
    DirectorDecision,
    MarketBar,
    MarketSnapshot,
    Quote,
)
from imie.runtime import (
    AnalysisCycleStatus,
    CompletedBarGuard,
    RuntimeConfig,
    SingleAnalysisCycle,
)
from imie.services import ContextBuilder

from imie.runtime import (
    SessionPolicy,
    SessionPolicyConfig,
)


class FakeMarketData:
    def get_quote(
        self,
        symbol: str,
    ):
        del symbol
        raise NotImplementedError

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ):
        del symbol
        del timeframe
        del limit
        raise NotImplementedError


class StaticMarketData:
    def __init__(
        self,
        *,
        quote: Quote,
        bars: list[MarketBar],
    ) -> None:
        self.quote = quote
        self.bars = bars
        self.quote_calls: list[str] = []
        self.bar_calls: list[
            tuple[str, str, int]
        ] = []

    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        self.quote_calls.append(
            symbol
        )
        return self.quote

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[MarketBar]:
        self.bar_calls.append(
            (
                symbol,
                timeframe,
                limit,
            )
        )
        return self.bars


class RaisingMarketData:
    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        del symbol

        raise RuntimeError(
            "Provider unavailable."
        )

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[MarketBar]:
        del symbol
        del timeframe
        del limit

        raise AssertionError(
            "get_bars should not be called."
        )


class FixedFreshnessGuard:
    def __init__(
        self,
        result: DataFreshness,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[MarketSnapshot, datetime | None]
        ] = []

    def evaluate(
        self,
        snapshot: MarketSnapshot,
        *,
        checked_at: datetime | None = None,
    ) -> DataFreshness:
        self.calls.append(
            (
                snapshot,
                checked_at,
            )
        )

        return self.result


class RecordingAnalysisPipeline:
    def __init__(
        self,
        decision: DecisionResult,
    ) -> None:
        self.decision = decision
        self.calls: list[
            tuple[object, DataFreshness]
        ] = []

    def evaluate(
        self,
        *,
        context,
        freshness: DataFreshness,
    ) -> DecisionResult:
        self.calls.append(
            (
                context,
                freshness,
            )
        )

        return self.decision


class RaisingAnalysisPipeline:
    def evaluate(
        self,
        *,
        context,
        freshness: DataFreshness,
    ) -> DecisionResult:
        del context
        del freshness

        raise ValueError(
            "Analysis pipeline failed."
        )


def test_cycle_can_be_created() -> None:
    config = RuntimeConfig()

    cycle = SingleAnalysisCycle(
        config=config,
        market_data=FakeMarketData(),
    )

    assert cycle.config is config
    assert cycle.market_data is not None
    assert cycle.completed_bar_guard is not None
    assert cycle.freshness_guard is not None
    assert cycle.context_builder is not None
    assert cycle.analysis_pipeline is not None


def test_config_must_be_runtime_config() -> None:
    with pytest.raises(
        TypeError,
        match="RuntimeConfig",
    ):
        SingleAnalysisCycle(
            config=object(),  # type: ignore[arg-type]
            market_data=FakeMarketData(),
        )


def test_market_data_must_provide_get_quote() -> None:
    class MissingQuote:
        def get_bars(
            self,
            symbol: str,
            timeframe: str,
            limit: int = 100,
        ):
            del symbol
            del timeframe
            del limit
            return []

    with pytest.raises(
        TypeError,
        match="get_quote",
    ):
        SingleAnalysisCycle(
            config=RuntimeConfig(),
            market_data=MissingQuote(),
        )


def make_permissive_session_policy() -> SessionPolicy:
    return SessionPolicy(
        SessionPolicyConfig(
            allow_premarket=True,
            allow_regular_session=True,
            allow_after_hours=True,
            allow_closed=True,
        )
    )


def test_market_data_must_provide_get_bars() -> None:
    class MissingBars:
        def get_quote(
            self,
            symbol: str,
        ):
            del symbol
            return None

    with pytest.raises(
        TypeError,
        match="get_bars",
    ):
        SingleAnalysisCycle(
            config=RuntimeConfig(),
            market_data=MissingBars(),
        )


BASE_TIME = datetime(
    2026,
    7,
    18,
    14,
    30,
    tzinfo=timezone.utc,
)


def make_quote(
    *,
    timestamp: datetime = BASE_TIME
    + timedelta(
        minutes=2,
        seconds=3,
    ),
) -> Quote:
    return Quote(
        symbol="NVDA",
        timestamp=timestamp,
        bid=100.00,
        ask=100.02,
        last=100.01,
        volume=100_000,
        provider="TEST",
    )


def make_bar(
    *,
    timestamp: datetime = BASE_TIME,
) -> MarketBar:
    return MarketBar(
        symbol="NVDA",
        timestamp=timestamp,
        open=99.50,
        high=100.25,
        low=99.25,
        close=100.00,
        volume=50_000,
        timeframe="2m",
        provider="TEST",
    )


def make_snapshot(
    *,
    quote: Quote | None = None,
    bars: list[MarketBar] | None = None,
) -> MarketSnapshot:
    resolved_quote = quote or make_quote()
    resolved_bars = bars or [
        make_bar(),
    ]

    return MarketSnapshot(
        symbol="NVDA",
        timestamp=resolved_quote.timestamp,
        quote=resolved_quote,
        bars=resolved_bars,
        timeframe="2m",
    )


def make_freshness(
    *,
    actionable: bool,
    checked_at: datetime = BASE_TIME
    + timedelta(
        minutes=2,
        seconds=3,
    ),
) -> DataFreshness:
    return DataFreshness(
        checked_at=checked_at,
        quote_timestamp=checked_at,
        latest_bar_timestamp=BASE_TIME,
        quote_age_seconds=0.0,
        bar_age_seconds=123.0,
        quote_bar_gap_seconds=123.0,
        quote_is_fresh=actionable,
        bar_is_fresh=actionable,
        timestamps_aligned=actionable,
        actionable=actionable,
        status=(
            "FRESH"
            if actionable
            else "STALE"
        ),
        reason=(
            "Quote and bar data are sufficiently synchronized."
            if actionable
            else "Latest quote is stale."
        ),
    )


def make_decision() -> DecisionResult:
    return DecisionResult(
        decision=DirectorDecision.PREPARE,
        actionable=False,
        confidence=90.0,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        reasons=(
            "Runtime pipeline test decision.",
        ),
        warnings=(),
        analyst_summary={},
        trade_plan=None,
        institutional_context=None,
    )

def test_run_completes_for_new_fresh_bar() -> None:
    checked_at = BASE_TIME + timedelta(
        minutes=2,
        seconds=3,
    )

    quote = make_quote(
        timestamp=checked_at,
    )

    bars = [
        make_bar(
            timestamp=BASE_TIME,
        ),
    ]

    market_data = StaticMarketData(
        quote=quote,
        bars=bars,
    )

    freshness = make_freshness(
        actionable=True,
        checked_at=checked_at,
    )

    freshness_guard = FixedFreshnessGuard(
        freshness
    )

    context_builder = ContextBuilder(
        atr_tolerance=0.25,
    )

    decision = make_decision()

    pipeline = RecordingAnalysisPipeline(
        decision
    )

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(
            symbol="NVDA",
            timeframe="2m",
            bar_limit=500,
            completion_delay_seconds=3.0,
        ),
        market_data=market_data,
        completed_bar_guard=CompletedBarGuard(
            timeframe_minutes=2,
            completion_delay_seconds=3.0,
        ),
        freshness_guard=freshness_guard,  # type: ignore[arg-type]
        context_builder=context_builder,
        analysis_pipeline=pipeline,  # type: ignore[arg-type]
        session_policy=make_permissive_session_policy(),
    )

    result = cycle.run(
        checked_at=checked_at,
    )

    assert result.status is AnalysisCycleStatus.COMPLETED
    assert result.succeeded is True
    assert result.completed_bar is not None
    assert result.completed_bar.accepted is True
    assert result.snapshot is not None
    assert result.freshness is freshness
    assert result.context is not None
    assert result.decision is decision

    assert market_data.quote_calls == [
        "NVDA",
    ]

    assert market_data.bar_calls == [
        (
            "NVDA",
            "2m",
            500,
        ),
    ]

    assert pipeline.calls == [
        (
            result.context,
            freshness,
        ),
    ]

def test_run_skips_incomplete_bar() -> None:
    checked_at = BASE_TIME + timedelta(
        minutes=2,
        seconds=2,
    )

    market_data = StaticMarketData(
        quote=make_quote(
            timestamp=checked_at,
        ),
        bars=[
            make_bar(
                timestamp=BASE_TIME,
            ),
        ],
    )

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(
            completion_delay_seconds=3.0,
        ),
        market_data=market_data,
        session_policy=make_permissive_session_policy(),
    )

    result = cycle.run(
        checked_at=checked_at,
    )

    assert (
        result.status
        is AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
    )
    assert result.skipped is True
    assert result.completed_bar is not None
    assert result.completed_bar.accepted is False
    assert result.completed_bar.is_complete is False
    assert (
        result.message
        == "Latest market bar has not completed."
    )

    assert result.snapshot is None
    assert result.freshness is None
    assert result.context is None
    assert result.decision is None


def test_run_skips_duplicate_completed_bar() -> None:
    checked_at = BASE_TIME + timedelta(
        minutes=2,
        seconds=3,
    )

    market_data = StaticMarketData(
        quote=make_quote(
            timestamp=checked_at,
        ),
        bars=[
            make_bar(
                timestamp=BASE_TIME,
            ),
        ],
    )

    freshness = make_freshness(
        actionable=True,
        checked_at=checked_at,
    )

    freshness_guard = FixedFreshnessGuard(
        freshness
    )

    pipeline = RecordingAnalysisPipeline(
        make_decision()
    )

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(
            completion_delay_seconds=3.0,
        ),
        market_data=market_data,
        freshness_guard=freshness_guard,  # type: ignore[arg-type]
        analysis_pipeline=pipeline,  # type: ignore[arg-type]
        session_policy=make_permissive_session_policy(),
    )

    first = cycle.run(
        checked_at=checked_at,
    )

    second = cycle.run(
        checked_at=checked_at
        + timedelta(
            seconds=5,
        ),
    )

    assert (
        first.status
        is AnalysisCycleStatus.COMPLETED
    )

    assert (
        second.status
        is AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
    )

    assert second.completed_bar is not None
    assert second.completed_bar.is_new is False
    assert (
        second.message
        == "Latest completed market bar was already processed."
    )

    assert len(
        pipeline.calls
    ) == 1


def test_run_returns_stale_data_result() -> None:
    checked_at = BASE_TIME + timedelta(
        minutes=2,
        seconds=3,
    )

    quote = make_quote(
        timestamp=checked_at,
    )

    bars = [
        make_bar(
            timestamp=BASE_TIME,
        ),
    ]

    stale_freshness = make_freshness(
        actionable=False,
        checked_at=checked_at,
    )

    freshness_guard = FixedFreshnessGuard(
        stale_freshness
    )

    pipeline = RecordingAnalysisPipeline(
        make_decision()
    )

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(
            completion_delay_seconds=3.0,
        ),
        market_data=StaticMarketData(
            quote=quote,
            bars=bars,
        ),
        freshness_guard=freshness_guard,  # type: ignore[arg-type]
        analysis_pipeline=pipeline,  # type: ignore[arg-type]
        session_policy=make_permissive_session_policy(),
    )

    result = cycle.run(
        checked_at=checked_at,
    )

    assert (
        result.status
        is AnalysisCycleStatus.STALE_DATA
    )
    assert result.succeeded is False
    assert result.skipped is False
    assert result.failed is False

    assert result.completed_bar is not None
    assert result.completed_bar.accepted is True
    assert result.snapshot is not None
    assert result.freshness is stale_freshness

    assert result.context is None
    assert result.decision is None
    assert result.message == stale_freshness.reason
    assert pipeline.calls == []


def test_run_returns_failed_result_for_provider_error() -> None:
    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=RaisingMarketData(),
        session_policy=make_permissive_session_policy(),
    )

    result = cycle.run(
        checked_at=BASE_TIME,
    )

    assert (
        result.status
        is AnalysisCycleStatus.FAILED
    )
    assert result.failed is True
    assert result.error_type == "RuntimeError"
    assert result.message == "Provider unavailable."

    assert result.completed_bar is None
    assert result.snapshot is None
    assert result.freshness is None
    assert result.context is None
    assert result.decision is None


def test_run_returns_failed_result_for_pipeline_error() -> None:
    checked_at = BASE_TIME + timedelta(
        minutes=2,
        seconds=3,
    )

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(
            completion_delay_seconds=3.0,
        ),
        market_data=StaticMarketData(
            quote=make_quote(
                timestamp=checked_at,
            ),
            bars=[
                make_bar(
                    timestamp=BASE_TIME,
                ),
            ],
        ),
        freshness_guard=FixedFreshnessGuard(
            make_freshness(
                actionable=True,
                checked_at=checked_at,
            )
        ),  # type: ignore[arg-type]
        analysis_pipeline=(
            RaisingAnalysisPipeline()
        ),  # type: ignore[arg-type]
        session_policy=make_permissive_session_policy(),
    )

    result = cycle.run(
        checked_at=checked_at,
    )

    assert (
        result.status
        is AnalysisCycleStatus.FAILED
    )
    assert result.error_type == "ValueError"
    assert result.message == "Analysis pipeline failed."


def test_run_rejects_timezone_naive_checked_at() -> None:
    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=FakeMarketData(),
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        cycle.run(
            checked_at=datetime(
                2026,
                7,
                18,
                14,
                30,
            ),
        )
        