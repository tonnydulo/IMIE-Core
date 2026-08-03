from __future__ import annotations

from pathlib import Path

from imie.config.settings import (
    AppSettings,
)
from imie.runtime.composite_result_publisher import (
    CompositeResultPublisher,
)
from imie.runtime.console_result_publisher import (
    ConsoleResultPublisher,
)
from imie.runtime.continuous_runtime_runner import (
    ContinuousRuntimeRunner,
)
from imie.runtime.json_lines_result_publisher import (
    JsonLinesResultPublisher,
)
from imie.runtime.runtime_application import (
    RuntimeApplication,
)
from imie.runtime.runtime_config import (
    RuntimeConfig,
)
from imie.runtime.interruptible_sleeper import (
    InterruptibleSleeper,
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
from imie.runtime.session_policy import (
    SessionPolicy,
)
from imie.runtime.market_session_clock import (
    MarketSessionClock,
)
from imie.runtime.nyse_calendar import (
    SUPPORTED_NYSE_CALENDAR_YEARS,
    build_nyse_calendar,
)
from imie.runtime.session_wake_planner import (
    SessionWakePlanner,
)
from imie.runtime.runtime_health_tracker import (
    RuntimeHealthTracker,
)
from imie.runtime.composite_health_publisher import (
    CompositeHealthPublisher,
)
from imie.runtime.console_health_publisher import (
    ConsoleHealthPublisher,
)
from imie.runtime.json_lines_health_publisher import (
    JsonLinesHealthPublisher,
)
from imie.runtime.dashboard_status_file_publisher import (
    DashboardStatusFilePublisher,
)

class RuntimeApplicationFactory:
    """
    Assembles the production IMIE runtime dependency graph.

    The factory creates objects only. It does not connect, run,
    sleep, print, or fetch market data.
    """

    @classmethod
    def create(
        cls,
        *,
        settings: AppSettings,
        config: RuntimeConfig | None = None,
        history_file: str | Path = (
            "runtime/history/imie_cycles.jsonl"
        ),
        console_output: bool = True,
        persist_history: bool = True,
        continue_on_publish_error: bool = True,
        session_policy: SessionPolicy | None = None,
        calendar_years: tuple[int, ...] | None = None,
        health_console_output: bool = True,
        health_history_file: str | Path = (
            "runtime/history/imie_health.jsonl"
        ),
        persist_health_history: bool = True,
        health_status_file: str | Path | None = None,
        health_status_indent: int | None = 2,
        create_health_status_parent_directories: bool = True,
    ) -> RuntimeApplication:
        if not isinstance(
            settings,
            AppSettings,
        ):
            raise TypeError(
                "settings must be an AppSettings."
            )

        if (
            config is not None
            and not isinstance(
                config,
                RuntimeConfig,
            )
        ):
            raise TypeError(
                "config must be a RuntimeConfig or None."
            )

        if not isinstance(
            console_output,
            bool,
        ):
            raise TypeError(
                "console_output must be a bool."
            )

        if not isinstance(
            persist_history,
            bool,
        ):
            raise TypeError(
                "persist_history must be a bool."
            )

        if not isinstance(
            continue_on_publish_error,
            bool,
        ):
            raise TypeError(
                "continue_on_publish_error must be a bool."
            )
        
        if not isinstance(
            health_console_output,
            bool,
        ):
            raise TypeError(
                "health_console_output must be a bool."
            )

        if not isinstance(
            persist_health_history,
            bool,
        ):
            raise TypeError(
                "persist_health_history must be a bool."
            )
        if (
            health_status_file is not None
            and not isinstance(
                health_status_file,
                str | Path,
            )
        ):
            raise TypeError(
                "health_status_file must be a string, "
                "Path, or None."
            )

        if (
            health_status_indent is not None
            and (
                isinstance(
                    health_status_indent,
                    bool,
                )
                or not isinstance(
                    health_status_indent,
                    int,
                )
            )
        ):
            raise TypeError(
                "health_status_indent must be an int or None."
            )

        if (
            health_status_indent is not None
            and health_status_indent < 0
        ):
            raise ValueError(
                "health_status_indent cannot be negative."
            )

        if not isinstance(
            create_health_status_parent_directories,
            bool,
        ):
            raise TypeError(
                "create_health_status_parent_directories "
                "must be a bool."
            )
        
        runtime_config = (
            config
            or RuntimeConfig()
        )

        health_publishers: list[
            object
        ] = []

        if health_console_output:
            health_publishers.append(
                ConsoleHealthPublisher()
            )

        if persist_health_history:
            health_publishers.append(
                JsonLinesHealthPublisher(
                    file_path=health_history_file,
                )
            )

        health_publisher = (
            CompositeHealthPublisher(
                publishers=health_publishers,
                continue_on_error=(
                    continue_on_publish_error
                ),
            )
            if health_publishers
            else None
        )

        dashboard_status_publisher = (
            DashboardStatusFilePublisher(
                path=health_status_file,
                symbol=runtime_config.symbol,
                timeframe=runtime_config.timeframe,
                indent=health_status_indent,
                create_parent_directories=(
                    create_health_status_parent_directories
                ),
            )
            if health_status_file is not None
            else None
        )

        health_tracker = RuntimeHealthTracker(
            publisher=health_publisher,
            status_publisher=(
                dashboard_status_publisher
            ),
        )

        resolved_calendar_years = (
            calendar_years
            if calendar_years is not None
            else SUPPORTED_NYSE_CALENDAR_YEARS
        )

       
        if not isinstance(
            resolved_calendar_years,
            tuple,
        ):
            raise TypeError(
                "calendar_years must be a tuple or None."
            )

        if not resolved_calendar_years:
            raise ValueError(
                "calendar_years cannot be empty."
            )

        market_data = MarketDataService(
            settings.default_provider
        )

              
        market_session_clock = MarketSessionClock(
            exchange_calendar=(
                build_nyse_calendar(
                    *resolved_calendar_years
                )
            )
        )

        resolved_session_policy = (
            session_policy
            or SessionPolicy()
        )

        session_wake_planner = SessionWakePlanner(
            market_session_clock=market_session_clock,
            session_policy=resolved_session_policy,
        )

        cycle = SingleAnalysisCycle(
            config=runtime_config,
            market_data=market_data,
            market_session_clock=market_session_clock,
            session_policy=resolved_session_policy,
        )


        publishers: list[
            object
        ] = []

        if console_output:
            publishers.append(
                ConsoleResultPublisher()
            )

        if persist_history:
            publishers.append(
                JsonLinesResultPublisher(
                    file_path=history_file,
                )
            )

        if dashboard_status_publisher is not None:
            publishers.append(
                dashboard_status_publisher
            )

        if not publishers:
            raise ValueError(
                "At least one runtime publisher must be enabled."
            )

        publisher = CompositeResultPublisher(
            publishers=publishers,
            continue_on_error=(
                continue_on_publish_error
            ),
        )

        one_shot_runner = RuntimeRunner(
            market_data=market_data,
            cycle=cycle,
        )

        interruptible_sleeper = (
            InterruptibleSleeper()
        )

        continuous_runner = ContinuousRuntimeRunner(
            config=runtime_config,
            market_data=market_data,
            cycle=cycle,
            publisher=publisher,
            session_wake_planner=session_wake_planner,
            interruptible_sleeper=interruptible_sleeper,
            health_tracker=health_tracker,
        )

        return RuntimeApplication(
            config=runtime_config,
            market_data=market_data,
            cycle=cycle,
            publisher=publisher,
            one_shot_runner=one_shot_runner,
            continuous_runner=continuous_runner,
        )