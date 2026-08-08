from __future__ import annotations

from dataclasses import dataclass

from imie.runtime.multi_symbol_cycle_runner import (
    MultiSymbolCycleRunner,
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
    runner: MultiSymbolCycleRunner

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
            self.runner,
            MultiSymbolCycleRunner,
        ):
            raise TypeError(
                "runner must be a MultiSymbolCycleRunner."
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

        if self.runner.universe is not self.universe:
            raise ValueError(
                "runner must use the application universe."
            )

        if self.runner.cycles != self.cycles:
            raise ValueError(
                "runner must use the application cycles."
            )