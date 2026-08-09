from __future__ import annotations

from dataclasses import dataclass

from imie.runtime.composite_result_publisher import (
    CompositeResultPublisher,
)
from imie.runtime.multi_symbol_cycle_runner import (
    MultiSymbolCycleRunner,
)
from imie.runtime.multi_symbol_runtime_runner import (
    MultiSymbolRuntimeRunner,
)
from imie.runtime.runtime_symbol_universe import (
    RuntimeSymbolUniverse,
)
from imie.runtime.single_analysis_cycle import (
    SingleAnalysisCycle,
)
from imie.services.market_data_service import (
    MarketDataService,
)
from imie.runtime.multi_symbol_continuous_runtime_runner import (
    MultiSymbolContinuousRuntimeRunner,
)


@dataclass(frozen=True, slots=True)
class MultiSymbolRuntimeApplication:
    """
    Assembled IMIE runtime application for a symbol universe.

    One market-data service is shared by all symbol-specific analysis
    cycles. Connection ownership remains outside the cycle runner.
    """

    universe: RuntimeSymbolUniverse
    market_data: MarketDataService
    cycles: tuple[
        SingleAnalysisCycle,
        ...,
    ]
    publisher: CompositeResultPublisher
    cycle_runner: MultiSymbolCycleRunner
    one_shot_runner: MultiSymbolRuntimeRunner
    continuous_runner: MultiSymbolContinuousRuntimeRunner

    def __post_init__(self) -> None:
        if not isinstance(
            self.universe,
            RuntimeSymbolUniverse,
        ):
            raise TypeError(
                "universe must be a RuntimeSymbolUniverse."
            )

        if not isinstance(
            self.market_data,
            MarketDataService,
        ):
            raise TypeError(
                "market_data must be a MarketDataService."
            )

        if not isinstance(
            self.cycles,
            tuple,
        ):
            raise TypeError(
                "cycles must be a tuple."
            )

        if not isinstance(
            self.continuous_runner,
            MultiSymbolContinuousRuntimeRunner,
        ):
            raise TypeError(
                "continuous_runner must be a "
                "MultiSymbolContinuousRuntimeRunner."
            )

        if not self.cycles:
            raise ValueError(
                "cycles cannot be empty."
            )

        for cycle in self.cycles:
            if not isinstance(
                cycle,
                SingleAnalysisCycle,
            ):
                raise TypeError(
                    "each cycle must be a SingleAnalysisCycle."
                )

        if not isinstance(
            self.publisher,
            CompositeResultPublisher,
        ):
            raise TypeError(
                "publisher must be a CompositeResultPublisher."
            )

        if not isinstance(
            self.cycle_runner,
            MultiSymbolCycleRunner,
        ):
            raise TypeError(
                "cycle_runner must be a MultiSymbolCycleRunner."
            )

        if not isinstance(
            self.one_shot_runner,
            MultiSymbolRuntimeRunner,
        ):
            raise TypeError(
                "one_shot_runner must be a MultiSymbolRuntimeRunner."
            )

        cycle_symbols = tuple(
            cycle.config.symbol
            for cycle in self.cycles
        )

        if cycle_symbols != self.universe.symbols:
            raise ValueError(
                "cycle symbols must match the runtime "
                "symbol universe in order."
            )

        for cycle in self.cycles:
            if cycle.market_data is not self.market_data:
                raise ValueError(
                    "all cycles must share the application "
                    "market_data instance."
                )

        if self.cycle_runner.universe is not self.universe:
            raise ValueError(
                "cycle_runner must use the application universe."
            )

        if self.cycle_runner.cycles != self.cycles:
            raise ValueError(
                "cycle_runner must use the application cycles."
            )

        if (
            self.one_shot_runner.runner
            is not self.cycle_runner
        ):
            raise ValueError(
                "one_shot_runner must use the application "
                "cycle_runner."
            )

        if (
            self.one_shot_runner.market_data
            is not self.market_data
        ):
            raise ValueError(
                "one_shot_runner must use the application "
                "market_data instance."
            )

        if (
            self.continuous_runner.runner
            is not self.cycle_runner
        ):
            raise ValueError(
                "continuous_runner must use the application "
                "cycle_runner."
            )

        if (
            self.continuous_runner.market_data
            is not self.market_data
        ):
            raise ValueError(
                "continuous_runner must use the application "
                "market_data instance."
            )