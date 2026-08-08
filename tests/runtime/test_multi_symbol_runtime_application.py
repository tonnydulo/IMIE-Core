import pytest

from imie.config.settings import (
    AppSettings,
)
from imie.runtime import (
    MultiSymbolCycleRunner,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SingleAnalysisCycle,
)
from imie.runtime.multi_symbol_runtime_application import (
    MultiSymbolRuntimeApplication,
)
from imie.services import (
    MarketDataService,
)


def make_market_data() -> MarketDataService:
    return MarketDataService(
        AppSettings(
            default_provider="mock",
        ).default_provider
    )


def make_application() -> MultiSymbolRuntimeApplication:
    market_data = make_market_data()

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

    runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=cycles,
    )

    return MultiSymbolRuntimeApplication(
        universe=universe,
        market_data=market_data,
        cycles=cycles,
        runner=runner,
    )


def test_application_preserves_multi_symbol_dependencies() -> None:
    application = make_application()

    assert application.universe.symbols == (
        "NVDA",
        "AMD",
        "SPY",
    )

    assert tuple(
        cycle.config.symbol
        for cycle in application.cycles
    ) == (
        "NVDA",
        "AMD",
        "SPY",
    )

    assert (
        application.runner.cycles
        == application.cycles
    )

    for cycle in application.cycles:
        assert (
            cycle.market_data
            is application.market_data
        )


def test_application_requires_runtime_symbol_universe() -> None:
    application = make_application()

    with pytest.raises(
        TypeError,
        match="RuntimeSymbolUniverse",
    ):
        MultiSymbolRuntimeApplication(
            universe=object(),  # type: ignore[arg-type]
            market_data=application.market_data,
            cycles=application.cycles,
            runner=application.runner,
        )


def test_application_requires_market_data_service() -> None:
    application = make_application()

    with pytest.raises(
        TypeError,
        match="MarketDataService",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=object(),  # type: ignore[arg-type]
            cycles=application.cycles,
            runner=application.runner,
        )


def test_application_rejects_mismatched_cycle_symbols() -> None:
    application = make_application()

    cycles = tuple(
        reversed(
            application.cycles
        )
    )

    with pytest.raises(
        ValueError,
        match="cycle symbols",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=application.market_data,
            cycles=cycles,
            runner=application.runner,
        )


def test_application_requires_shared_market_data() -> None:
    application = make_application()

    other_market_data = make_market_data()

    cycles = (
        SingleAnalysisCycle(
            config=RuntimeConfig(
                symbol="NVDA",
            ),
            market_data=other_market_data,
        ),
        *application.cycles[1:],
    )

    runner = MultiSymbolCycleRunner(
        universe=application.universe,
        cycles=cycles,
    )

    with pytest.raises(
        ValueError,
        match="share",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=application.market_data,
            cycles=cycles,
            runner=runner,
        )


def test_application_requires_runner_to_use_same_universe() -> None:
    application = make_application()

    other_universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    runner = MultiSymbolCycleRunner(
        universe=other_universe,
        cycles=application.cycles,
    )

    with pytest.raises(
        ValueError,
        match="application universe",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=application.market_data,
            cycles=application.cycles,
            runner=runner,
        )