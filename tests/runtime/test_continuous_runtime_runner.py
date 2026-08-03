import pytest
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    ContinuousRuntimeRunner,
    RuntimeConfig,
    RuntimeHealthSnapshot,
    RuntimeHealthState,
    RuntimeHealthTracker,
    SingleAnalysisCycle,
    MarketSessionResult,
    MarketSessionState,
    SessionPolicyAction,
    SessionPolicyResult,
    MarketSessionClock,
    SessionPolicy,
    SessionWakePlanner,
    InterruptibleSleeper,
    build_nyse_calendar,
)


class FakeMarketData:
    def connect(
        self,
    ) -> None:
        pass

    def disconnect(
        self,
    ) -> None:
        pass

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


CHECKED_AT_1 = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)

CHECKED_AT_2 = datetime(
    2026,
    7,
    18,
    14,
    32,
    8,
    tzinfo=timezone.utc,
)

CHECKED_AT_3 = datetime(
    2026,
    7,
    18,
    14,
    32,
    13,
    tzinfo=timezone.utc,
)


def make_result(
    message: str,
) -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT_1,
        completed_at=CHECKED_AT_1,
        message=message,
    )


class RecordingMarketData:
    def __init__(
        self,
        *,
        connect_error: Exception | None = None,
        disconnect_error: Exception | None = None,
    ) -> None:
        self.connect_error = connect_error
        self.disconnect_error = disconnect_error

        self.connect_calls = 0
        self.disconnect_calls = 0

    def connect(
        self,
    ) -> None:
        self.connect_calls += 1

        if self.connect_error is not None:
            raise self.connect_error

    def disconnect(
        self,
    ) -> None:
        self.disconnect_calls += 1

        if self.disconnect_error is not None:
            raise self.disconnect_error

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


class SequencedCycle(
    SingleAnalysisCycle,
):
    def __init__(
        self,
        *,
        market_data: object,
        results: list[
            AnalysisCycleResult
        ],
    ) -> None:
        super().__init__(
            config=RuntimeConfig(),
            market_data=market_data,
        )

        self.results = list(
            results
        )

        self.run_calls: list[
            datetime | None
        ] = []

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        self.run_calls.append(
            checked_at
        )

        if not self.results:
            raise RuntimeError(
                "No more configured cycle results."
            )

        return self.results.pop(
            0
        )


class RaisingCycle(
    SingleAnalysisCycle,
):
    def __init__(
        self,
        *,
        market_data: object,
        error: Exception,
    ) -> None:
        super().__init__(
            config=RuntimeConfig(),
            market_data=market_data,
        )

        self.error = error
        self.run_calls = 0

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        del checked_at

        self.run_calls += 1

        raise self.error


class RecordingSleep:
    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(
        self,
        seconds: float,
    ) -> None:
        self.calls.append(
            seconds
        )


class RecordingPublisher:
    def __init__(
        self,
    ) -> None:
        self.results: list[
            AnalysisCycleResult
        ] = []

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.results.append(
            result
        )


def make_cycle(
    market_data: object,
) -> SingleAnalysisCycle:
    return SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=market_data,
    )


def make_runner(
    *,
    config: RuntimeConfig | None = None,
    health_tracker: RuntimeHealthTracker | None = None,
    sleep_function=None,
) -> ContinuousRuntimeRunner:
    market_data = RecordingMarketData()

    return ContinuousRuntimeRunner(
        config=config or RuntimeConfig(),
        market_data=market_data,
        cycle=make_cycle(
            market_data
        ),
        health_tracker=health_tracker,
        sleep_function=(
            sleep_function
            if sleep_function is not None
            else lambda seconds: None
        ),
    )



def make_session_skipped_result() -> AnalysisCycleResult:
    checked_at = datetime(
        2026,
        7,
        19,
        16,
        0,
        tzinfo=timezone.utc,
    )

    market_session = MarketSessionResult(
        state=MarketSessionState.CLOSED,
        checked_at=checked_at,
        market_time=checked_at.astimezone(
            ZoneInfo(
                "America/New_York"
            )
        ),
        is_trading_day=False,
        reason="The exchange is closed.",
    )

    session_policy = SessionPolicyResult(
        action=SessionPolicyAction.SKIP,
        session=market_session,
        reason=(
            "Runtime analysis is disabled during "
            "the CLOSED session."
        ),
    )
  
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.SKIPPED_SESSION,
        symbol="NVDA",
        timeframe="2m",
        started_at=checked_at,
        completed_at=checked_at,
        message=session_policy.reason,
        market_session=market_session,
        session_policy=session_policy,
    )

def make_wake_planner() -> SessionWakePlanner:
    return SessionWakePlanner(
        market_session_clock=MarketSessionClock(
            exchange_calendar=(
                build_nyse_calendar()
            )
        ),
        session_policy=SessionPolicy(),
    )
    

def test_runner_can_be_created() -> None:
    config = RuntimeConfig()
    market_data = FakeMarketData()
    cycle = make_cycle(
        market_data
    )

    runner = ContinuousRuntimeRunner(
        config=config,
        market_data=market_data,
        cycle=cycle,
    )

    assert runner.config is config
    assert runner.market_data is market_data
    assert runner.cycle is cycle
    assert runner.publisher is None
    assert runner.running is False
    assert runner.stop_requested is False
    assert runner.completed_cycle_count == 0


def test_config_must_be_runtime_config() -> None:
    market_data = FakeMarketData()

    with pytest.raises(
        TypeError,
        match="RuntimeConfig",
    ):
        ContinuousRuntimeRunner(
            config=object(),  # type: ignore[arg-type]
            market_data=market_data,
            cycle=make_cycle(
                market_data
            ),
        )


def test_market_data_must_provide_connect() -> None:
    class MissingConnect:
        def disconnect(
            self,
        ) -> None:
            pass

    with pytest.raises(
        TypeError,
        match="connect",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=MissingConnect(),
            cycle=make_cycle(
                FakeMarketData()
            ),
        )


def test_market_data_must_provide_disconnect() -> None:
    class MissingDisconnect:
        def connect(
            self,
        ) -> None:
            pass

    with pytest.raises(
        TypeError,
        match="disconnect",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=MissingDisconnect(),
            cycle=make_cycle(
                FakeMarketData()
            ),
        )


def test_cycle_must_be_single_analysis_cycle() -> None:
    with pytest.raises(
        TypeError,
        match="SingleAnalysisCycle",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=FakeMarketData(),
            cycle=object(),  # type: ignore[arg-type]
        )


def test_publisher_must_be_callable() -> None:
    market_data = FakeMarketData()

    with pytest.raises(
        TypeError,
        match="publisher",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=market_data,
            cycle=make_cycle(
                market_data
            ),
            publisher=object(),  # type: ignore[arg-type]
        )


def test_sleep_function_must_be_callable() -> None:
    market_data = FakeMarketData()

    with pytest.raises(
        TypeError,
        match="sleep_function",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=market_data,
            cycle=make_cycle(
                market_data
            ),
            sleep_function=object(),  # type: ignore[arg-type]
        )

def test_run_executes_multiple_cycles_with_one_connection() -> None:
    market_data = RecordingMarketData()

    expected = [
        make_result(
            "Cycle 1",
        ),
        make_result(
            "Cycle 2",
        ),
        make_result(
            "Cycle 3",
        ),
    ]

    cycle = SequencedCycle(
        market_data=market_data,
        results=expected.copy(),
    )

    sleep_recorder = RecordingSleep()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=5.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_recorder,
    )

    results = runner.run(
        max_cycles=3,
    )

    assert results == tuple(
        expected
    )

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1

    assert len(
        cycle.run_calls
    ) == 3

    assert runner.running is False

def test_sleep_occurs_only_between_cycles() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
            make_result(
                "Cycle 3",
            ),
        ],
    )

    sleep_recorder = RecordingSleep()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=7.5,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_recorder,
    )

    runner.run(
        max_cycles=3,
    )

    assert sleep_recorder.calls == [
        7.5,
        7.5,
    ]

def test_publisher_receives_every_cycle_result() -> None:
    market_data = RecordingMarketData()

    expected = [
        make_result(
            "Cycle 1",
        ),
        make_result(
            "Cycle 2",
        ),
    ]

    cycle = SequencedCycle(
        market_data=market_data,
        results=expected.copy(),
    )

    publisher = RecordingPublisher()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        publisher=publisher,
        sleep_function=lambda seconds: None,
    )

    results = runner.run(
        max_cycles=2,
    )

    assert results == tuple(
        expected
    )

    assert publisher.results == expected


def test_publisher_can_request_stop() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
            make_result(
                "Cycle 3",
            ),
        ],
    )

    sleep_recorder = RecordingSleep()

    runner: ContinuousRuntimeRunner

    def stop_after_first(
        result: AnalysisCycleResult,
    ) -> None:
        del result
        runner.request_stop()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        publisher=stop_after_first,
        sleep_function=sleep_recorder,
    )

    results = runner.run(
        max_cycles=3,
    )

    assert len(
        results
    ) == 1

    assert results[0].message == "Cycle 1"

    assert runner.stop_requested is True
    assert runner.running is False

    assert sleep_recorder.calls == []

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1


def test_checked_at_provider_sequences_cycle_times() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
            make_result(
                "Cycle 3",
            ),
        ],
    )

    timestamps = iter(
        [
            CHECKED_AT_1,
            CHECKED_AT_2,
            CHECKED_AT_3,
        ]
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    runner.run(
        max_cycles=3,
        checked_at_provider=lambda: next(
            timestamps
        ),
    )

    assert cycle.run_calls == [
        CHECKED_AT_1,
        CHECKED_AT_2,
        CHECKED_AT_3,
    ]

def test_cycle_exception_disconnects_and_propagates() -> None:
    market_data = RecordingMarketData()

    cycle = RaisingCycle(
        market_data=market_data,
        error=RuntimeError(
            "Unexpected programming failure."
        ),
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        RuntimeError,
        match="Unexpected programming failure",
    ):
        runner.run(
            max_cycles=3,
        )

    assert cycle.run_calls == 1
    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1
    assert runner.running is False

def test_connection_failure_propagates_without_disconnect() -> None:
    market_data = RecordingMarketData(
        connect_error=ConnectionError(
            "Unable to connect."
        )
    )

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        ConnectionError,
        match="Unable to connect",
    ):
        runner.run(
            max_cycles=1,
        )

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 0
    assert cycle.run_calls == []
    assert runner.running is False

def test_disconnect_failure_propagates() -> None:
    market_data = RecordingMarketData(
        disconnect_error=RuntimeError(
            "Disconnect failed."
        )
    )

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        RuntimeError,
        match="Disconnect failed",
    ):
        runner.run(
            max_cycles=1,
        )

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1
    assert runner.running is False

@pytest.mark.parametrize(
    "max_cycles",
    [
        0,
        -1,
    ],
)
def test_max_cycles_must_be_positive(
    max_cycles: int,
) -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        ValueError,
        match="max_cycles",
    ):
        runner.run(
            max_cycles=max_cycles,
        )


@pytest.mark.parametrize(
    "max_cycles",
    [
        True,
        1.5,
        "2",
    ],
)
def test_max_cycles_must_be_int_or_none(
    max_cycles: object,
) -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        TypeError,
        match="max_cycles",
    ):
        runner.run(
            max_cycles=max_cycles,  # type: ignore[arg-type]
        )

def test_checked_at_provider_must_be_callable() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    with pytest.raises(
        TypeError,
        match="checked_at_provider",
    ):
        runner.run(
            max_cycles=1,
            checked_at_provider=object(),  # type: ignore[arg-type]
        )

def test_closed_session_sleeps_until_next_session() -> None:
    market_data = RecordingMarketData()
    sleep_recorder = RecordingSleep()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_session_skipped_result(),
            make_session_skipped_result(),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=5.0,
            closed_session_polling_interval_seconds=300.0,
            heartbeat_interval_seconds=60000.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_recorder,
        session_wake_planner=make_wake_planner(),
    )

    runner.run(
        max_cycles=2,
    )

    assert sleep_recorder.calls == [
        57600.0,
    ]

def test_closed_session_uses_fallback_without_planner() -> None:
    market_data = RecordingMarketData()
    sleep_recorder = RecordingSleep()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_session_skipped_result(),
            make_session_skipped_result(),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            closed_session_polling_interval_seconds=300.0,
            heartbeat_interval_seconds=301.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_recorder,
    )

    runner.run(
        max_cycles=2,
    )

    assert sleep_recorder.calls == [
        300.0,
    ]


def test_active_cycle_uses_normal_polling_interval() -> None:
    market_data = RecordingMarketData()

    sleep_recorder = RecordingSleep()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=5.0,
            closed_session_polling_interval_seconds=300.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_recorder,
    )

    runner.run(
        max_cycles=2,
    )

    assert sleep_recorder.calls == [
        5.0,
    ]

def test_polling_interval_requires_cycle_result() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
    )

    with pytest.raises(
        TypeError,
        match="AnalysisCycleResult",
    ):
        runner._polling_interval_for(
            object(),  # type: ignore[arg-type]
        )


def test_stop_request_during_sleep_prevents_next_cycle() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
        ],
    )

    runner: ContinuousRuntimeRunner

    def sleep_and_request_stop(
        seconds: float,
    ) -> None:
        assert seconds == 5.0
        runner.request_stop()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=5.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=sleep_and_request_stop,
    )

    results = runner.run(
        max_cycles=2,
    )

    assert len(
        results
    ) == 1

    assert results[0].message == "Cycle 1"
    assert runner.stop_requested is True
    assert runner.running is False

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1

def test_interruptible_sleeper_must_be_valid() -> None:
    market_data = FakeMarketData()

    with pytest.raises(
        TypeError,
        match="InterruptibleSleeper",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=market_data,
            cycle=make_cycle(
                market_data
            ),
            interruptible_sleeper=object(),  # type: ignore[arg-type]
        )

def test_request_stop_interrupts_sleeper() -> None:
    market_data = RecordingMarketData()
    sleeper = InterruptibleSleeper()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        interruptible_sleeper=sleeper,
    )

    runner.request_stop()

    assert runner.stop_requested is True
    assert sleeper.interrupted is True


class StopRequestSleeper(
    InterruptibleSleeper
):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.runner: ContinuousRuntimeRunner | None = None
        self.wait_calls: list[float] = []

    def wait(
        self,
        seconds: float,
    ) -> bool:
        self.wait_calls.append(
            seconds
        )

        if self.runner is None:
            raise RuntimeError(
                "Runner was not assigned."
            )

        self.runner.request_stop()

        return super().wait(
            seconds
        )
    
def test_interruptible_sleep_stops_before_next_cycle() -> None:
    market_data = RecordingMarketData()
    sleeper = StopRequestSleeper()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=3600.0,
            heartbeat_interval_seconds=3601.0,
        ),
        market_data=market_data,
        cycle=cycle,
        interruptible_sleeper=sleeper,
    )

    sleeper.runner = runner

    results = runner.run(
        max_cycles=2,
    )

    assert len(
        results
    ) == 1
    assert sleeper.wait_calls == [
        3600.0,
    ]
    assert runner.stop_requested is True
    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1


def test_runner_records_successful_lifecycle() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    tracker = RuntimeHealthTracker()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        health_tracker=tracker,
    )

    runner.run(
        max_cycles=1,
    )

    states = tuple(
        snapshot.state
        for snapshot in tracker.history
    )

    assert states == (
        RuntimeHealthState.CREATED,
        RuntimeHealthState.STARTING,
        RuntimeHealthState.CONNECTED,
        RuntimeHealthState.RUNNING,
        RuntimeHealthState.STOPPED,
    )

    assert tracker.current.cycle_count == 1

def test_runner_records_failed_lifecycle() -> None:
    market_data = RecordingMarketData()

    cycle = RaisingCycle(
        market_data=market_data,
        error=RuntimeError(
            "Cycle failed."
        ),
    )

    tracker = RuntimeHealthTracker()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        health_tracker=tracker,
    )

    with pytest.raises(
        RuntimeError,
        match="Cycle failed",
    ):
        runner.run(
            max_cycles=1,
        )

    assert (
        tracker.current.state
        is RuntimeHealthState.FAILED
    )

    assert (
        tracker.current.error_type
        == "RuntimeError"
    )

def test_runner_records_sleeping_state() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
        ],
    )

    tracker = RuntimeHealthTracker()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(
            polling_interval_seconds=5.0,
        ),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
        health_tracker=tracker,
    )

    runner.run(
        max_cycles=2,
    )

    states = tuple(
        snapshot.state
        for snapshot in tracker.history
    )

    assert RuntimeHealthState.SLEEPING in states

def test_health_tracker_must_be_valid() -> None:
    market_data = FakeMarketData()

    with pytest.raises(
        TypeError,
        match="RuntimeHealthTracker",
    ):
        ContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=market_data,
            cycle=make_cycle(
                market_data
            ),
            health_tracker=object(),  # type: ignore[arg-type]
        )

def test_runner_tracks_completed_cycle_count() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
            make_result(
                "Cycle 3",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        sleep_function=lambda seconds: None,
    )

    runner.run(
        max_cycles=3,
    )

    assert runner.completed_cycle_count == 3


def test_completed_cycle_count_resets_for_new_run() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Run 1",
            ),
        ],
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
    )

    runner.run(
        max_cycles=1,
    )

    assert runner.completed_cycle_count == 1

    runner.cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Run 2",
            ),
            make_result(
                "Run 3",
            ),
        ],
    )

    runner.run(
        max_cycles=2,
    )

    assert runner.completed_cycle_count == 2

def test_stopping_health_uses_completed_cycle_count() -> None:
    market_data = RecordingMarketData()
    tracker = RuntimeHealthTracker()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
            make_result(
                "Cycle 2",
            ),
        ],
    )

    runner: ContinuousRuntimeRunner

    def stop_after_first(
        result: AnalysisCycleResult,
    ) -> None:
        del result
        runner.request_stop()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        publisher=stop_after_first,
        health_tracker=tracker,
    )

    runner.run(
        max_cycles=2,
    )

    stopping_snapshots = tuple(
        snapshot
        for snapshot in tracker.history
        if (
            snapshot.state
            is RuntimeHealthState.STOPPING
        )
    )

    assert len(
        stopping_snapshots
    ) == 1

    assert (
        stopping_snapshots[0].cycle_count
        == 1
    )

    assert runner.completed_cycle_count == 1


def test_failed_cycle_is_not_counted_as_completed() -> None:
    market_data = RecordingMarketData()
    tracker = RuntimeHealthTracker()

    cycle = RaisingCycle(
        market_data=market_data,
        error=RuntimeError(
            "Cycle failed."
        ),
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        health_tracker=tracker,
    )

    with pytest.raises(
        RuntimeError,
        match="Cycle failed",
    ):
        runner.run(
            max_cycles=1,
        )

    assert runner.completed_cycle_count == 0
    assert tracker.current.cycle_count == 0

class RecordingHealthPublisher:
    def __init__(
        self,
    ) -> None:
        self.snapshots: list[
            RuntimeHealthSnapshot
        ] = []

    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        self.snapshots.append(
            snapshot
        )

def test_long_wait_emits_periodic_heartbeats() -> None:
    waits: list[float] = []
    health_publisher = RecordingHealthPublisher()

    tracker = RuntimeHealthTracker(
        publisher=health_publisher,
    )

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=60.0,
        ),
        health_tracker=tracker,
        sleep_function=waits.append,
    )

    runner._wait_with_heartbeats(
        150.0
    )

    assert waits == [
        60.0,
        60.0,
        30.0,
    ]

    heartbeats = [
        snapshot
        for snapshot
        in health_publisher.snapshots
        if (
            snapshot.message
            == (
                "Runtime remains responsive "
                "while sleeping."
            )
        )
    ]

    assert len(
        heartbeats
    ) == 2


def test_short_wait_does_not_emit_heartbeat() -> None:
    waits: list[float] = []
    health_publisher = RecordingHealthPublisher()

    tracker = RuntimeHealthTracker(
        publisher=health_publisher,
    )

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=60.0,
        ),
        health_tracker=tracker,
        sleep_function=waits.append,
    )

    published_before = len(
        health_publisher.snapshots
    )

    runner._wait_with_heartbeats(
        30.0
    )

    assert waits == [
        30.0,
    ]

    assert len(
        health_publisher.snapshots
    ) == published_before


def test_wait_equal_to_interval_has_no_heartbeat() -> None:
    waits: list[float] = []
    health_publisher = RecordingHealthPublisher()

    tracker = RuntimeHealthTracker(
        publisher=health_publisher,
    )

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=60.0,
        ),
        health_tracker=tracker,
        sleep_function=waits.append,
    )

    published_before = len(
        health_publisher.snapshots
    )

    runner._wait_with_heartbeats(
        60.0
    )

    assert waits == [
        60.0,
    ]

    assert len(
        health_publisher.snapshots
    ) == published_before


def test_heartbeat_uses_live_completed_cycle_count() -> None:
    waits: list[float] = []
    health_publisher = RecordingHealthPublisher()

    tracker = RuntimeHealthTracker(
        publisher=health_publisher,
    )

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=10.0,
        ),
        health_tracker=tracker,
        sleep_function=waits.append,
    )

    runner._completed_cycle_count = 4

    runner._wait_with_heartbeats(
        25.0
    )

    heartbeats = [
        snapshot
        for snapshot
        in health_publisher.snapshots
        if snapshot.message.startswith(
            "Runtime remains responsive"
        )
    ]

    assert [
        snapshot.cycle_count
        for snapshot in heartbeats
    ] == [
        4,
        4,
    ]


def test_shutdown_stops_heartbeat_wait_chunks() -> None:
    waits: list[float] = []

    runner: ContinuousRuntimeRunner

    def sleep_and_stop(
        seconds: float,
    ) -> None:
        waits.append(
            seconds
        )

        runner.request_stop()

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=60.0,
        ),
        sleep_function=sleep_and_stop,
    )

    runner._wait_with_heartbeats(
        300.0
    )

    assert waits == [
        60.0,
    ]

    assert runner.stop_requested is True


class RaisingHealthPublisher:
    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        if snapshot.message.startswith(
            "Runtime remains responsive"
        ):
            raise RuntimeError(
                "Heartbeat output failed."
            )
        

def test_heartbeat_publisher_failure_does_not_stop_wait() -> None:
    waits: list[float] = []

    tracker = RuntimeHealthTracker(
        publisher=RaisingHealthPublisher(),
    )

    runner = make_runner(
        config=RuntimeConfig(
            heartbeat_interval_seconds=10.0,
        ),
        health_tracker=tracker,
        sleep_function=waits.append,
    )

    runner._wait_with_heartbeats(
        25.0
    )

    assert waits == [
        10.0,
        10.0,
        5.0,
    ]


def test_successful_cycle_records_completion_time() -> None:
    market_data = RecordingMarketData()

    cycle = SequencedCycle(
        market_data=market_data,
        results=[
            make_result(
                "Cycle 1",
            ),
        ],
    )

    completed_at = datetime(
        2026,
        7,
        22,
        15,
        0,
        tzinfo=timezone.utc,
    )

    tracker = RuntimeHealthTracker(
        clock=lambda: completed_at,
    )

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        health_tracker=tracker,
    )

    runner.run(
        max_cycles=1,
    )

    assert (
        tracker.last_successful_cycle_at
        == completed_at
    )


def test_failed_cycle_does_not_record_success_time() -> None:
    market_data = RecordingMarketData()

    cycle = RaisingCycle(
        market_data=market_data,
        error=RuntimeError(
            "Cycle failed."
        ),
    )

    tracker = RuntimeHealthTracker()

    runner = ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
        health_tracker=tracker,
    )

    with pytest.raises(
        RuntimeError,
        match="Cycle failed",
    ):
        runner.run(
            max_cycles=1,
        )

    assert (
        tracker.last_successful_cycle_at
        is None
    )

    