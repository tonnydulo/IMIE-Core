from datetime import (
    datetime,
    timezone,
)

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SingleAnalysisCycle,
)
from imie.runtime.multi_symbol_cycle_runner import (
    MultiSymbolCycleRunner,
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


class RecordingCycle(
    SingleAnalysisCycle,
):
    def __init__(
        self,
        *,
        symbol: str,
    ) -> None:
        super().__init__(
            config=RuntimeConfig(
                symbol=symbol,
            ),
            market_data=FakeMarketData(),
        )

        self.checked_at_calls: list[
            datetime | None
        ] = []

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> AnalysisCycleResult:
        self.checked_at_calls.append(
            checked_at
        )

        resolved_time = (
            checked_at
            or CHECKED_AT
        )

        return AnalysisCycleResult(
            status=(
                AnalysisCycleStatus
                .SKIPPED_NO_NEW_BAR
            ),
            symbol=self.config.symbol,
            timeframe=self.config.timeframe,
            started_at=resolved_time,
            completed_at=resolved_time,
            message="No new completed bar.",
        )


def test_runner_runs_each_symbol_in_universe_order() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    cycles = (
        RecordingCycle(
            symbol="NVDA",
        ),
        RecordingCycle(
            symbol="AMD",
        ),
        RecordingCycle(
            symbol="SPY",
        ),
    )

    runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=cycles,
    )

    results = runner.run(
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

    for cycle in cycles:
        assert cycle.checked_at_calls == [
            CHECKED_AT,
        ]


def test_runner_requires_runtime_symbol_universe() -> None:
    with pytest.raises(
        TypeError,
        match="RuntimeSymbolUniverse",
    ):
        MultiSymbolCycleRunner(
            universe=object(),  # type: ignore[arg-type]
            cycles=(
                RecordingCycle(
                    symbol="NVDA",
                ),
            ),
        )


def test_cycles_must_be_tuple() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
        )
    )

    with pytest.raises(
        TypeError,
        match="cycles must be a tuple",
    ):
        MultiSymbolCycleRunner(
            universe=universe,
            cycles=[  # type: ignore[arg-type]
                RecordingCycle(
                    symbol="NVDA",
                ),
            ],
        )


def test_cycles_cannot_be_empty() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
        )
    )

    with pytest.raises(
        ValueError,
        match="cycles cannot be empty",
    ):
        MultiSymbolCycleRunner(
            universe=universe,
            cycles=(),
        )


def test_each_cycle_must_be_single_analysis_cycle() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
        )
    )

    with pytest.raises(
        TypeError,
        match="SingleAnalysisCycle",
    ):
        MultiSymbolCycleRunner(
            universe=universe,
            cycles=(
                object(),  # type: ignore[arg-type]
            ),
        )


def test_cycle_symbols_must_match_universe_order() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
        )
    )

    with pytest.raises(
        ValueError,
        match="cycle symbols",
    ):
        MultiSymbolCycleRunner(
            universe=universe,
            cycles=(
                RecordingCycle(
                    symbol="AMD",
                ),
                RecordingCycle(
                    symbol="NVDA",
                ),
            ),
        )