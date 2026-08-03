from __future__ import annotations

from dataclasses import dataclass

from imie.runtime.composite_result_publisher import (
    CompositeResultPublisher,
)
from imie.runtime.continuous_runtime_runner import (
    ContinuousRuntimeRunner,
)
from imie.runtime.runtime_config import (
    RuntimeConfig,
)
from imie.runtime.runtime_runner import (
    RuntimeRunner,
)
from imie.runtime.single_analysis_cycle import (
    SingleAnalysisCycle,
)
from imie.services.market_data_service import (
    MarketDataService,
)
from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeApplication:
    """
    Fully assembled IMIE runtime application.

    Construction does not connect to a provider or execute a cycle.
    """

    config: RuntimeConfig
    market_data: MarketDataService
    cycle: SingleAnalysisCycle
    publisher: CompositeResultPublisher
    one_shot_runner: RuntimeRunner
    continuous_runner: ContinuousRuntimeRunner

    def __post_init__(self) -> None:
        if not isinstance(
            self.config,
            RuntimeConfig,
        ):
            raise TypeError(
                "config must be a RuntimeConfig."
            )

        if not isinstance(
            self.market_data,
            MarketDataService,
        ):
            raise TypeError(
                "market_data must be a MarketDataService."
            )

        if not isinstance(
            self.cycle,
            SingleAnalysisCycle,
        ):
            raise TypeError(
                "cycle must be a SingleAnalysisCycle."
            )

        if not isinstance(
            self.publisher,
            CompositeResultPublisher,
        ):
            raise TypeError(
                "publisher must be a CompositeResultPublisher."
            )

        if not isinstance(
            self.one_shot_runner,
            RuntimeRunner,
        ):
            raise TypeError(
                "one_shot_runner must be a RuntimeRunner."
            )

        if not isinstance(
            self.continuous_runner,
            ContinuousRuntimeRunner,
        ):
            raise TypeError(
                "continuous_runner must be a "
                "ContinuousRuntimeRunner."
            )
        
    @property
    def runtime_health(
        self,
    ) -> RuntimeHealthSnapshot:
        return (
            self.continuous_runner
            .health_tracker
            .current
        )
    
    @property
    def health_summary(
        self,
    ) -> RuntimeHealthSummary:
        return (
            self.continuous_runner
            .health_tracker
            .summary()
        )

    @property
    def health_status(
        self,
    ) -> dict[str, Any]:
        return self.health_summary.to_dict()


    @property
    def runtime_health_history(
        self,
    ) -> tuple[RuntimeHealthSnapshot, ...]:
        return (
            self.continuous_runner
            .health_tracker
            .history
        )


    @property
    def completed_cycle_count(
        self,
    ) -> int:
        return (
            self.continuous_runner
            .completed_cycle_count
        )
    

    def health_status_json(
        self,
        *,
        indent: int | None = None,
    ) -> str:
        return self.health_summary.to_json(
            indent=indent
        )