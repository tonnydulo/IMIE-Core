import pytest

from datetime import datetime, timezone

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    RuntimeConfig,
    RuntimeRunner,
    SingleAnalysisCycle,
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


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


def make_skipped_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.SKIPPED_NO_NEW_BAR,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="No new completed bar.",
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


class FixedCycle(
    SingleAnalysisCycle,
):
    def __init__(
        self,
        *,
        market_data: object,
        result: AnalysisCycleResult,
    ) -> None:
        super().__init__(
            config=RuntimeConfig(),
            market_data=market_data,
        )

        self.result = result
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

        return self.result


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


def make_cycle(
    market_data: object,
) -> SingleAnalysisCycle:
    return SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=market_data,
    )


def test_runner_can_be_created() -> None:
    market_data = FakeMarketData()

    cycle = make_cycle(
        market_data
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    assert runner.market_data is market_data
    assert runner.cycle is cycle


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
        RuntimeRunner(
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
        RuntimeRunner(
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
        RuntimeRunner(
            market_data=FakeMarketData(),
            cycle=object(),  # type: ignore[arg-type]
        )

def test_run_once_connects_runs_and_disconnects() -> None:
    market_data = RecordingMarketData()
    expected = make_skipped_result()

    cycle = FixedCycle(
        market_data=market_data,
        result=expected,
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    result = runner.run_once(
        checked_at=CHECKED_AT,
    )

    assert result is expected

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1

    assert cycle.run_calls == [
        CHECKED_AT,
    ]

def test_run_once_disconnects_when_cycle_raises() -> None:
    market_data = RecordingMarketData()

    cycle = RaisingCycle(
        market_data=market_data,
        error=RuntimeError(
            "Cycle execution failed."
        ),
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    result = runner.run_once(
        checked_at=CHECKED_AT,
    )

    assert (
        result.status
        is AnalysisCycleStatus.FAILED
    )
    assert result.failed is True
    assert result.error_type == "RuntimeError"
    assert result.message == "Cycle execution failed."

    assert result.symbol == "NVDA"
    assert result.timeframe == "2m"

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1
    assert cycle.run_calls == 1


def test_run_once_returns_failed_when_connect_fails() -> None:
    market_data = RecordingMarketData(
        connect_error=ConnectionError(
            "Provider connection failed."
        )
    )

    cycle = FixedCycle(
        market_data=market_data,
        result=make_skipped_result(),
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    result = runner.run_once(
        checked_at=CHECKED_AT,
    )

    assert (
        result.status
        is AnalysisCycleStatus.FAILED
    )
    assert result.error_type == "ConnectionError"
    assert result.message == "Provider connection failed."

    assert market_data.connect_calls == 1

    # Connection never completed, so disconnect is not attempted.
    assert market_data.disconnect_calls == 0

    assert cycle.run_calls == []


def test_disconnect_failure_does_not_replace_result() -> None:
    market_data = RecordingMarketData(
        disconnect_error=RuntimeError(
            "Disconnect failed."
        )
    )

    expected = make_skipped_result()

    cycle = FixedCycle(
        market_data=market_data,
        result=expected,
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    result = runner.run_once(
        checked_at=CHECKED_AT,
    )

    assert result is expected

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1
    assert cycle.run_calls == [
        CHECKED_AT,
    ]


def test_timezone_naive_checked_at_is_rejected() -> None:
    market_data = RecordingMarketData()

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=market_data,
    )

    runner = RuntimeRunner(
        market_data=market_data,
        cycle=cycle,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        runner.run_once(
            checked_at=datetime(
                2026,
                7,
                18,
                14,
                32,
                3,
            ),
        )

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1


