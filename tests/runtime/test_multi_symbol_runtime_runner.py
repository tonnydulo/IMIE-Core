from datetime import (
    datetime,
    timezone,
)

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    MultiSymbolCycleRunner,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SingleAnalysisCycle,
)
from imie.runtime.multi_symbol_runtime_runner import (
    MultiSymbolRuntimeRunner,
)


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


class RecordingMarketData:
    def __init__(self) -> None:
        self.connect_calls = 0
        self.disconnect_calls = 0

    def connect(
        self,
    ) -> None:
        self.connect_calls += 1

    def disconnect(
        self,
    ) -> None:
        self.disconnect_calls += 1

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


class RecordingCycle(
    SingleAnalysisCycle,
):
    def __init__(
        self,
        *,
        symbol: str,
        market_data: object,
    ) -> None:
        super().__init__(
            config=RuntimeConfig(
                symbol=symbol,
            ),
            market_data=market_data,
        )

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        resolved = checked_at or CHECKED_AT

        return AnalysisCycleResult(
            status=(
                AnalysisCycleStatus
                .SKIPPED_NO_NEW_BAR
            ),
            symbol=self.config.symbol,
            timeframe=self.config.timeframe,
            started_at=resolved,
            completed_at=resolved,
            message="No new completed bar.",
        )


def make_runner(
    market_data: RecordingMarketData,
) -> MultiSymbolRuntimeRunner:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    cycles = tuple(
        RecordingCycle(
            symbol=symbol,
            market_data=market_data,
        )
        for symbol in universe
    )

    cycle_runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=cycles,
    )

    return MultiSymbolRuntimeRunner(
        market_data=market_data,
        runner=cycle_runner,
    )


def test_run_once_connects_once_runs_all_symbols_and_disconnects() -> None:
    market_data = RecordingMarketData()

    runner = make_runner(
        market_data
    )

    results = runner.run_once(
        checked_at=CHECKED_AT,
    )

    assert tuple(
        result.symbol
        for result in results
    ) == (
        "NVDA",
        "AMD",
        "SPY",
    )

    assert market_data.connect_calls == 1
    assert market_data.disconnect_calls == 1


def test_runner_requires_connect() -> None:
    class MissingConnect:
        def disconnect(self) -> None:
            pass

    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
        )
    )

    cycle_runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=(
            RecordingCycle(
                symbol="NVDA",
                market_data=RecordingMarketData(),
            ),
        ),
    )

    with pytest.raises(
        TypeError,
        match="connect",
    ):
        MultiSymbolRuntimeRunner(
            market_data=MissingConnect(),
            runner=cycle_runner,
        )


def test_runner_requires_disconnect() -> None:
    class MissingDisconnect:
        def connect(self) -> None:
            pass

    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
        )
    )

    cycle_runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=(
            RecordingCycle(
                symbol="NVDA",
                market_data=RecordingMarketData(),
            ),
        ),
    )

    with pytest.raises(
        TypeError,
        match="disconnect",
    ):
        MultiSymbolRuntimeRunner(
            market_data=MissingDisconnect(),
            runner=cycle_runner,
        )


def test_runner_requires_multi_symbol_cycle_runner() -> None:
    with pytest.raises(
        TypeError,
        match="MultiSymbolCycleRunner",
    ):
        MultiSymbolRuntimeRunner(
            market_data=RecordingMarketData(),
            runner=object(),  # type: ignore[arg-type]
        )
