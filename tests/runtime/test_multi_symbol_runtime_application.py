import pytest

from imie.config.settings import (
    AppSettings,
)

from imie.providers.mock_provider import MockProvider

from imie.runtime import (
    MultiSymbolCycleRunner,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SingleAnalysisCycle,
    MultiSymbolRuntimeRunner
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

    cycle_runner = MultiSymbolCycleRunner(
        universe=universe,
        cycles=cycles,
    )

    one_shot_runner = MultiSymbolRuntimeRunner(
        market_data=market_data,
        runner=cycle_runner,
    )

    return MultiSymbolRuntimeApplication(
        universe=universe,
        market_data=market_data,
        cycles=cycles,
        cycle_runner=cycle_runner,
        one_shot_runner=one_shot_runner,
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
        application.cycle_runner.cycles
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
            cycle_runner=application.cycle_runner,
            one_shot_runner=application.one_shot_runner,
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
            cycle_runner=application.cycle_runner,
            one_shot_runner=application.one_shot_runner,
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
            cycle_runner=application.cycle_runner,
            one_shot_runner=application.one_shot_runner,
        )


def test_application_requires_shared_market_data() -> None:
    application = make_application()

    other_market_data = MarketDataService(
        "mock"
    )

    cycles = tuple(
        SingleAnalysisCycle(
            config=cycle.config,
            market_data=other_market_data,
            market_session_clock=cycle.market_session_clock,
            session_policy=cycle.session_policy,
        )
        for cycle in application.cycles
    )

    cycle_runner = MultiSymbolCycleRunner(
        universe=application.universe,
        cycles=cycles,
    )

    one_shot_runner = MultiSymbolRuntimeRunner(
        market_data=application.market_data,
        runner=cycle_runner,
    )

    with pytest.raises(
        ValueError,
        match="share",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=application.market_data,
            cycles=cycles,
            cycle_runner=cycle_runner,
            one_shot_runner=one_shot_runner,
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

    cycle_runner = MultiSymbolCycleRunner(
        universe=other_universe,
        cycles=application.cycles,
    )

    one_shot_runner = MultiSymbolRuntimeRunner(
        market_data=application.market_data,
        runner=cycle_runner,
    )

    with pytest.raises(
        ValueError,
        match="application universe",
    ):
        MultiSymbolRuntimeApplication(
            universe=application.universe,
            market_data=application.market_data,
            cycles=application.cycles,
            cycle_runner=cycle_runner,
            one_shot_runner=one_shot_runner,
        )
