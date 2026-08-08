from __future__ import annotations

from datetime import datetime

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.multi_symbol_cycle_runner import (
    MultiSymbolCycleRunner,
)


class MultiSymbolRuntimeRunner:
    """
    Executes one multi-symbol runtime pass using one provider connection.

    The shared market-data service is connected once, all configured
    symbol cycles are executed, and the provider is disconnected once.
    """

    def __init__(
        self,
        *,
        market_data: object,
        runner: MultiSymbolCycleRunner,
    ) -> None:
        if not callable(
            getattr(
                market_data,
                "connect",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide connect()."
            )

        if not callable(
            getattr(
                market_data,
                "disconnect",
                None,
            )
        ):
            raise TypeError(
                "market_data must provide disconnect()."
            )

        if not isinstance(
            runner,
            MultiSymbolCycleRunner,
        ):
            raise TypeError(
                "runner must be a MultiSymbolCycleRunner."
            )

        self.market_data = market_data
        self.runner = runner

    def run_once(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> tuple[
        AnalysisCycleResult,
        ...,
    ]:
        connected = False

        try:
            self.market_data.connect()
            connected = True

            return self.runner.run(
                checked_at=checked_at,
            )

        finally:
            if connected:
                self.market_data.disconnect()