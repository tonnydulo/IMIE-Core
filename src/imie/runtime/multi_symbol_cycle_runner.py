from __future__ import annotations

from datetime import datetime

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.runtime_symbol_universe import (
    RuntimeSymbolUniverse,
)
from imie.runtime.single_analysis_cycle import (
    SingleAnalysisCycle,
)


class MultiSymbolCycleRunner:
    """
    Runs one SingleAnalysisCycle for each symbol in a runtime universe.

    This runner does not connect or disconnect market data. Provider
    connection ownership remains outside this orchestration layer.
    """

    def __init__(
        self,
        *,
        universe: RuntimeSymbolUniverse,
        cycles: tuple[
            SingleAnalysisCycle,
            ...,
        ],
    ) -> None:
        if not isinstance(
            universe,
            RuntimeSymbolUniverse,
        ):
            raise TypeError(
                "universe must be a RuntimeSymbolUniverse."
            )

        if not isinstance(
            cycles,
            tuple,
        ):
            raise TypeError(
                "cycles must be a tuple."
            )

        if not cycles:
            raise ValueError(
                "cycles cannot be empty."
            )

        for cycle in cycles:
            if not isinstance(
                cycle,
                SingleAnalysisCycle,
            ):
                raise TypeError(
                    "each cycle must be a SingleAnalysisCycle."
                )

        cycle_symbols = tuple(
            cycle.config.symbol
            for cycle in cycles
        )

        if cycle_symbols != universe.symbols:
            raise ValueError(
                "cycle symbols must match the runtime "
                "symbol universe in order."
            )

        self.universe = universe
        self.cycles = cycles

    def run(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> tuple[
        AnalysisCycleResult,
        ...,
    ]:
        return tuple(
            cycle.run(
                checked_at=checked_at,
            )
            for cycle in self.cycles
        )