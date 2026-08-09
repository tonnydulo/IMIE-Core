from __future__ import annotations

import pytest

from imie.runtime import (
    MultiSymbolContinuousRuntimeRunner,
    MultiSymbolCycleRunner,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SingleAnalysisCycle,
)
from imie.services import (
    MarketDataService,
)


class RecordingMarketData:
    def __init__(self) -> None:
        self.connect_count = 0
        self.disconnect_count = 0

    def connect(self) -> None:
        self.connect_count += 1

    def disconnect(self) -> None:
        self.disconnect_count += 1


def make_cycle_runner() -> MultiSymbolCycleRunner:
    market_data = MarketDataService(
        "mock"
    )

    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    cycles = tuple(
        SingleAnalysisCycle(
            config=RuntimeConfig(
                symbol=symbol,
            ),
            market_data=market_data,
        )
        for symbol in universe
    )

    return MultiSymbolCycleRunner(
        universe=universe,
        cycles=cycles,
    )


def test_runner_connects_once_and_disconnects_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    market_data = RecordingMarketData()
    cycle_runner = make_cycle_runner()

    run_count = 0

    def fake_run(
        *,
        checked_at=None,
    ):
        nonlocal run_count
        run_count += 1
        return ()

    monkeypatch.setattr(
        cycle_runner,
        "run",
        fake_run,
    )

    runner = MultiSymbolContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        runner=cycle_runner,
    )

    results = runner.run(
        max_cycles=1,
    )

    assert results == ()
    assert run_count == 1
    assert market_data.connect_count == 1
    assert market_data.disconnect_count == 1
    assert runner.completed_cycle_count == 1
    assert runner.running is False


def test_runner_repeats_full_universe_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    market_data = RecordingMarketData()
    cycle_runner = make_cycle_runner()

    source_cycle = cycle_runner.cycles[0]

    sample_result = source_cycle.run()

    run_count = 0

    def fake_run(
        *,
        checked_at=None,
    ):
        nonlocal run_count
        run_count += 1

        return (
            sample_result,
        )

    monkeypatch.setattr(
        cycle_runner,
        "run",
        fake_run,
    )

    runner = MultiSymbolContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        runner=cycle_runner,
        sleep_function=lambda _: None,
    )

    results = runner.run(
        max_cycles=3,
    )

    assert run_count == 3
    assert runner.completed_cycle_count == 3

    assert len(results) == 3

    assert market_data.connect_count == 1
    assert market_data.disconnect_count == 1


def test_runner_disconnects_when_cycle_runner_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    market_data = RecordingMarketData()
    cycle_runner = make_cycle_runner()

    def fake_run(
        *,
        checked_at=None,
    ):
        raise RuntimeError(
            "cycle failure"
        )

    monkeypatch.setattr(
        cycle_runner,
        "run",
        fake_run,
    )

    runner = MultiSymbolContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        runner=cycle_runner,
    )

    with pytest.raises(
        RuntimeError,
        match="cycle failure",
    ):
        runner.run(
            max_cycles=1,
        )

    assert market_data.connect_count == 1
    assert market_data.disconnect_count == 1
    assert runner.running is False


def test_runner_requires_runtime_config() -> None:
    with pytest.raises(
        TypeError,
        match="RuntimeConfig",
    ):
        MultiSymbolContinuousRuntimeRunner(
            config=object(),  # type: ignore[arg-type]
            market_data=RecordingMarketData(),
            runner=make_cycle_runner(),
        )


def test_runner_requires_market_data_connect() -> None:
    class MissingConnect:
        def disconnect(self) -> None:
            pass

    with pytest.raises(
        TypeError,
        match=r"connect\(\)",
    ):
        MultiSymbolContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=MissingConnect(),
            runner=make_cycle_runner(),
        )


def test_runner_requires_market_data_disconnect() -> None:
    class MissingDisconnect:
        def connect(self) -> None:
            pass

    with pytest.raises(
        TypeError,
        match=r"disconnect\(\)",
    ):
        MultiSymbolContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=MissingDisconnect(),
            runner=make_cycle_runner(),
        )


def test_runner_requires_multi_symbol_cycle_runner() -> None:
    with pytest.raises(
        TypeError,
        match="MultiSymbolCycleRunner",
    ):
        MultiSymbolContinuousRuntimeRunner(
            config=RuntimeConfig(),
            market_data=RecordingMarketData(),
            runner=object(),  # type: ignore[arg-type]
        )


def test_runner_validates_max_cycles() -> None:
    runner = MultiSymbolContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=RecordingMarketData(),
        runner=make_cycle_runner(),
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        runner.run(
            max_cycles=0,
        )

    with pytest.raises(
        TypeError,
        match="int or None",
    ):
        runner.run(
            max_cycles=True,  # type: ignore[arg-type]
        )