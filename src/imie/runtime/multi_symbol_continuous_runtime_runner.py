from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from time import sleep

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)
from imie.runtime.interruptible_sleeper import (
    InterruptibleSleeper,
)
from imie.runtime.multi_symbol_cycle_runner import (
    MultiSymbolCycleRunner,
)
from imie.runtime.runtime_config import (
    RuntimeConfig,
)
from imie.runtime.runtime_health_state import (
    RuntimeHealthState,
)
from imie.runtime.runtime_health_tracker import (
    RuntimeHealthTracker,
)
from imie.runtime.session_wake_planner import (
    SessionWakePlanner,
)


class MultiSymbolContinuousRuntimeRunner:
    """
    Runs repeated multi-symbol IMIE analysis passes.

    The market-data provider is connected once before the loop and
    disconnected once after the loop.

    Each completed runtime cycle represents one pass across the full
    configured symbol universe.
    """

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        market_data: object,
        runner: MultiSymbolCycleRunner,
        publisher: Callable[
            [AnalysisCycleResult],
            None,
        ]
        | None = None,
        session_wake_planner: SessionWakePlanner | None = None,
        interruptible_sleeper: InterruptibleSleeper | None = None,
        health_tracker: RuntimeHealthTracker | None = None,
        sleep_function: Callable[
            [float],
            None,
        ] = sleep,
    ) -> None:
        if not isinstance(
            config,
            RuntimeConfig,
        ):
            raise TypeError(
                "config must be a RuntimeConfig."
            )

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

        if (
            publisher is not None
            and not callable(
                publisher
            )
        ):
            raise TypeError(
                "publisher must be callable or None."
            )

        if not callable(
            sleep_function
        ):
            raise TypeError(
                "sleep_function must be callable."
            )

        if (
            session_wake_planner is not None
            and not isinstance(
                session_wake_planner,
                SessionWakePlanner,
            )
        ):
            raise TypeError(
                "session_wake_planner must be a "
                "SessionWakePlanner or None."
            )

        if (
            interruptible_sleeper is not None
            and not isinstance(
                interruptible_sleeper,
                InterruptibleSleeper,
            )
        ):
            raise TypeError(
                "interruptible_sleeper must be an "
                "InterruptibleSleeper or None."
            )

        if (
            health_tracker is not None
            and not isinstance(
                health_tracker,
                RuntimeHealthTracker,
            )
        ):
            raise TypeError(
                "health_tracker must be a "
                "RuntimeHealthTracker or None."
            )

        self.config = config
        self.market_data = market_data
        self.runner = runner
        self.publisher = publisher
        self.session_wake_planner = session_wake_planner
        self.interruptible_sleeper = interruptible_sleeper
        self.health_tracker = (
            health_tracker
            or RuntimeHealthTracker()
        )
        self.sleep_function = sleep_function

        self._stop_requested = False
        self._running = False
        self._completed_cycle_count = 0

    def run(
        self,
        *,
        max_cycles: int | None = None,
        checked_at_provider: Callable[
            [],
            datetime | None,
        ]
        | None = None,
    ) -> tuple[AnalysisCycleResult, ...]:
        self._validate_max_cycles(
            max_cycles
        )

        if (
            checked_at_provider is not None
            and not callable(
                checked_at_provider
            )
        ):
            raise TypeError(
                "checked_at_provider must be callable or None."
            )

        if self._running:
            raise RuntimeError(
                "MultiSymbolContinuousRuntimeRunner "
                "is already running."
            )

        self._stop_requested = False
        self._completed_cycle_count = 0

        if self.interruptible_sleeper is not None:
            self.interruptible_sleeper.reset()

        self._running = True

        results: list[
            AnalysisCycleResult
        ] = []

        cycle_count = 0
        connected = False

        self._record_health(
            RuntimeHealthState.STARTING,
            cycle_count=cycle_count,
            message=(
                "Multi-symbol continuous runtime "
                "is starting."
            ),
        )

        try:
            self.market_data.connect()
            connected = True

            self._record_health(
                RuntimeHealthState.CONNECTED,
                cycle_count=cycle_count,
                message=(
                    "Market-data connection established."
                ),
            )

            while not self._stop_requested:
                if (
                    max_cycles is not None
                    and cycle_count >= max_cycles
                ):
                    break

                self._record_health(
                    RuntimeHealthState.RUNNING,
                    cycle_count=cycle_count,
                    message=(
                        "Multi-symbol runtime cycle "
                        "is running."
                    ),
                )

                checked_at = (
                    checked_at_provider()
                    if checked_at_provider is not None
                    else None
                )

                cycle_results = self.runner.run(
                    checked_at=checked_at,
                )

                results.extend(
                    cycle_results
                )

                cycle_count += 1
                self._completed_cycle_count = (
                    cycle_count
                )

                self.health_tracker.record_successful_cycle(
                    cycle_count=(
                        self._completed_cycle_count
                    ),
                )

                if self.publisher is not None:
                    for result in cycle_results:
                        self.publisher(
                            result
                        )

                if self._stop_requested:
                    break

                if (
                    max_cycles is not None
                    and cycle_count >= max_cycles
                ):
                    break

                polling_interval = (
                    self._polling_interval_for(
                        cycle_results
                    )
                )

                self._record_health(
                    RuntimeHealthState.SLEEPING,
                    cycle_count=cycle_count,
                    message=(
                        "Runtime is waiting before "
                        "the next multi-symbol cycle."
                    ),
                )

                self._wait_for_next_cycle(
                    polling_interval
                )

        except BaseException as error:
            self._record_health(
                RuntimeHealthState.FAILED,
                cycle_count=(
                    self._completed_cycle_count
                ),
                message=(
                    "Multi-symbol continuous runtime "
                    "failed."
                ),
                error=error,
            )

            raise

        finally:
            if connected:
                try:
                    self.market_data.disconnect()
                finally:
                    self._running = False
            else:
                self._running = False

            if (
                self.health_tracker.current.state
                is not RuntimeHealthState.FAILED
            ):
                self._record_health(
                    RuntimeHealthState.STOPPED,
                    cycle_count=cycle_count,
                    message=(
                        "Multi-symbol continuous "
                        "runtime stopped."
                    ),
                )

        return tuple(
            results
        )

    def _polling_interval_for(
        self,
        results: tuple[
            AnalysisCycleResult,
            ...,
        ],
    ) -> float:
        if not isinstance(
            results,
            tuple,
        ):
            raise TypeError(
                "results must be a tuple."
            )

        if not results:
            raise ValueError(
                "results cannot be empty."
            )

        for result in results:
            if not isinstance(
                result,
                AnalysisCycleResult,
            ):
                raise TypeError(
                    "each result must be an "
                    "AnalysisCycleResult."
                )

        skipped_results = tuple(
            result
            for result in results
            if result.status
            is AnalysisCycleStatus.SKIPPED_SESSION
        )

        if not skipped_results:
            return (
                self.config.polling_interval_seconds
            )

        session_result = skipped_results[0]

        if (
            self.session_wake_planner is None
            or session_result.market_session is None
        ):
            return (
                self.config
                .closed_session_polling_interval_seconds
            )

        wake_result = (
            self.session_wake_planner.evaluate(
                session_result
                .market_session
                .checked_at
            )
        )

        if (
            not wake_result.resolved
            or wake_result.delay_seconds is None
        ):
            return (
                self.config
                .closed_session_polling_interval_seconds
            )

        return max(
            1.0,
            wake_result.delay_seconds,
        )

    def request_stop(
        self,
    ) -> None:
        self._stop_requested = True

        self._record_health(
            RuntimeHealthState.STOPPING,
            cycle_count=(
                self._completed_cycle_count
            ),
            message=(
                "Runtime shutdown was requested."
            ),
        )

        if self.interruptible_sleeper is not None:
            self.interruptible_sleeper.interrupt()

    @property
    def stop_requested(
        self,
    ) -> bool:
        return self._stop_requested

    @property
    def running(
        self,
    ) -> bool:
        return self._running

    @property
    def completed_cycle_count(
        self,
    ) -> int:
        return self._completed_cycle_count

    @staticmethod
    def _validate_max_cycles(
        value: int | None,
    ) -> None:
        if value is None:
            return

        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "max_cycles must be an int or None."
            )

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "max_cycles must be an int or None."
            )

        if value < 1:
            raise ValueError(
                "max_cycles must be at least 1."
            )

    def _wait_for_next_cycle(
        self,
        seconds: float,
    ) -> None:
        if isinstance(
            seconds,
            bool,
        ) or not isinstance(
            seconds,
            int | float,
        ):
            raise TypeError(
                "seconds must be a number."
            )

        resolved_seconds = float(
            seconds
        )

        if resolved_seconds < 0.0:
            raise ValueError(
                "seconds cannot be negative."
            )

        if self.interruptible_sleeper is not None:
            self.interruptible_sleeper.wait(
                resolved_seconds
            )
            return

        self.sleep_function(
            resolved_seconds
        )

    def _record_health(
        self,
        state: RuntimeHealthState,
        *,
        cycle_count: int,
        message: str,
        error: BaseException | None = None,
    ) -> None:
        self.health_tracker.transition(
            state,
            cycle_count=cycle_count,
            message=message,
            error=error,
        )