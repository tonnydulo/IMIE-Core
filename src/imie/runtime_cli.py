from __future__ import annotations

import argparse
import logging

from dataclasses import replace
from pathlib import Path
from imie.runtime import RuntimeShutdownController

from typing import Sequence

from imie.config.settings import (
    AppSettings,
    load_settings,
)
from imie.runtime.nyse_calendar import (
    SUPPORTED_NYSE_CALENDAR_YEARS,
)
from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    RuntimeApplication,
    RuntimeApplicationFactory,
    RuntimeConfig,
    RuntimeSymbolUniverse,
    SessionPolicy,
    SessionPolicyConfig,
)
from imie.utils.logging_utils import (
    configure_logging,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-runtime",
        description=(
            "Run the Institutional Market Intelligence "
            "Engine runtime."
        ),
    )

    parser.add_argument(
        "--symbol",
        default="NVDA",
        help="Market symbol to analyze. Default: NVDA.",
    )

    parser.add_argument(
        "--symbols",
        nargs="+",
        default=None,
        help=(
            "Market symbols to include in the runtime symbol universe. "
            "Example: --symbols NVDA AMD SPY."
        ),
    )

    parser.add_argument(
        "--provider",
        default=None,
        choices=(
            "mock",
            "alpaca",
        ),
        help=(
            "Override the configured market-data provider. "
            "Supported values: mock, alpaca."
        ),
    )

    parser.add_argument(
        "--calendar-years",
        type=int,
        nargs="+",
        choices=SUPPORTED_NYSE_CALENDAR_YEARS,
        default=None,
        help=(
            "NYSE calendar years to load. "
            "Supported values: 2026, 2027, 2028. "
            "Default: all supported years."
        ),
    )

    parser.add_argument(
        "--timeframe",
        default="2m",
        choices=(
            "1m",
            "2m",
            "5m",
            "15m",
        ),
        help="Bar timeframe. Default: 2m.",
    )

    parser.add_argument(
        "--bar-limit",
        type=int,
        default=500,
        help="Number of bars to request. Default: 500.",
    )

    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=5.0,
        help=(
            "Polling interval for continuous mode. "
            "Default: 5 seconds."
        ),
    )

    parser.add_argument(
        "--closed-poll-seconds",
        type=float,
        default=300.0,
        help=(
            "Polling interval while runtime analysis is "
            "blocked by the market-session policy. "
            "Default: 300 seconds."
        ),
    )

    parser.add_argument(
        "--completion-delay",
        type=float,
        default=3.0,
        help=(
            "Seconds to wait after a candle boundary before "
            "considering the bar complete. Default: 3."
        ),
    )

    parser.add_argument(
        "--allow-after-hours",
        action="store_true",
        help=(
            "Allow runtime analysis during the "
            "after-hours session."
        ),
    )

    parser.add_argument(
        "--allow-closed",
        action="store_true",
        help=(
            "Allow runtime analysis when the configured "
            "market session is closed."
        ),
    )

    parser.add_argument(
        "--disable-premarket",
        action="store_true",
        help=(
            "Disable runtime analysis during the "
            "premarket session."
        ),
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run repeated analysis cycles.",
    )

    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help=(
            "Maximum continuous cycles. Omit to run until "
            "interrupted."
        ),
    )

    parser.add_argument(
        "--history-file",
        type=Path,
        default=Path(
            "runtime/history/imie_cycles.jsonl"
        ),
        help=(
            "JSON Lines output file. Default: "
            "runtime/history/imie_cycles.jsonl."
        ),
    )

    parser.add_argument(
        "--no-console",
        action="store_true",
        help="Disable console result publishing.",
    )

    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Disable JSON Lines history persistence.",
    )

    parser.add_argument(
        "--health-history-file",
        type=Path,
        default=Path(
            "runtime/history/imie_health.jsonl"
        ),
        help=(
            "Runtime health JSON Lines file. Default: "
            "runtime/history/imie_health.jsonl."
        ),
    )

    parser.add_argument(
        "--no-health-console",
        action="store_true",
        help=(
            "Disable runtime health transition output "
            "on the console."
        ),
    )

    parser.add_argument(
        "--heartbeat-seconds",
        type=float,
        default=60.0,
        help=(
            "Heartbeat interval during long runtime waits. "
            "Default: 60 seconds."
        ),
    )

    parser.add_argument(
        "--no-health-history",
        action="store_true",
        help=(
            "Disable runtime health JSON Lines "
            "persistence."
        ),
    )

    parser.add_argument(
        "--health-status-file",
        type=Path,
        default=None,
        help=(
            "Write the latest runtime health summary to "
            "a JSON file. Disabled by default."
        ),
    )

    parser.add_argument(
        "--health-status-indent",
        type=int,
        default=2,
        help=(
            "JSON indentation for the health-status file. "
            "Default: 2."
        ),
    )

    parser.add_argument(
        "--no-health-status-parent-directories",
        action="store_true",
        help=(
            "Do not automatically create parent directories "
            "for the health-status file."
        ),
    )

    return parser


def build_runtime_config(
    arguments: argparse.Namespace,
) -> RuntimeConfig:
    return RuntimeConfig(
        symbol=arguments.symbol,
        timeframe=arguments.timeframe,
        bar_limit=arguments.bar_limit,
        polling_interval_seconds=(
            arguments.poll_seconds
        ),
        closed_session_polling_interval_seconds=(
            arguments.closed_poll_seconds
        ),
        completion_delay_seconds=(
            arguments.completion_delay
        ),
        heartbeat_interval_seconds=(
            arguments.heartbeat_seconds
        ),
    )

def build_runtime_symbol_universe(
    arguments: argparse.Namespace,
) -> RuntimeSymbolUniverse:
    symbols = getattr(
        arguments,
        "symbols",
        None,
    )

    if symbols is None:
        return RuntimeSymbolUniverse(
            symbols=(
                arguments.symbol,
            )
        )

    return RuntimeSymbolUniverse(
        symbols=tuple(
            symbols
        )
    )


def resolve_settings(
    *,
    settings: AppSettings,
    arguments: argparse.Namespace,
) -> AppSettings:
    if not isinstance(
        settings,
        AppSettings,
    ):
        raise TypeError(
            "settings must be an AppSettings."
        )

    provider = getattr(
        arguments,
        "provider",
        None,
    )

    if provider is None:
        return settings

    if not isinstance(
        provider,
        str,
    ):
        raise TypeError(
            "provider must be a string or None."
        )

    normalized_provider = (
        provider
        .strip()
        .lower()
    )

    if normalized_provider not in {
        "mock",
        "alpaca",
    }:
        raise ValueError(
            "provider must be mock or alpaca."
        )

    return replace(
        settings,
        default_provider=normalized_provider,
    )


def resolve_calendar_years(
    arguments: argparse.Namespace,
) -> tuple[int, ...]:
    if not isinstance(
        arguments,
        argparse.Namespace,
    ):
        raise TypeError(
            "arguments must be an argparse.Namespace."
        )

    calendar_years = getattr(
        arguments,
        "calendar_years",
        None,
    )

    if calendar_years is None:
        return SUPPORTED_NYSE_CALENDAR_YEARS

    if not isinstance(
        calendar_years,
        list,
    ):
        raise TypeError(
            "calendar_years must be a list or None."
        )

    if not calendar_years:
        raise ValueError(
            "calendar_years cannot be empty."
        )

    normalized_years: list[int] = []

    for year in calendar_years:
        if isinstance(
            year,
            bool,
        ) or not isinstance(
            year,
            int,
        ):
            raise TypeError(
                "calendar_years must contain "
                "only integers."
            )

        if (
            year
            not in SUPPORTED_NYSE_CALENDAR_YEARS
        ):
            supported = ", ".join(
                str(value)
                for value
                in SUPPORTED_NYSE_CALENDAR_YEARS
            )

            raise ValueError(
                "Unsupported NYSE calendar year "
                f"{year}. Supported years: "
                f"{supported}."
            )

        if year not in normalized_years:
            normalized_years.append(
                year
            )

    return tuple(
        normalized_years
    )

def build_session_policy(
    arguments: argparse.Namespace,
) -> SessionPolicy:
    if not isinstance(
        arguments,
        argparse.Namespace,
    ):
        raise TypeError(
            "arguments must be an argparse.Namespace."
        )

    allow_after_hours = getattr(
        arguments,
        "allow_after_hours",
        False,
    )

    allow_closed = getattr(
        arguments,
        "allow_closed",
        False,
    )

    disable_premarket = getattr(
        arguments,
        "disable_premarket",
        False,
    )

    for name, value in (
        (
            "allow_after_hours",
            allow_after_hours,
        ),
        (
            "allow_closed",
            allow_closed,
        ),
        (
            "disable_premarket",
            disable_premarket,
        ),
    ):
        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be a bool."
            )

    return SessionPolicy(
        SessionPolicyConfig(
            allow_premarket=not disable_premarket,
            allow_regular_session=True,
            allow_after_hours=allow_after_hours,
            allow_closed=allow_closed,
        )
    )


def build_application(
    *,
    settings: AppSettings,
    arguments: argparse.Namespace,
) -> RuntimeApplication:
    config = build_runtime_config(
        arguments
    )

    resolved_settings = resolve_settings(
        settings=settings,
        arguments=arguments,
    )

    session_policy = build_session_policy(
        arguments
    )

    calendar_years = resolve_calendar_years(
        arguments
    )

    return RuntimeApplicationFactory.create(
        settings=resolved_settings,
        config=config,
        history_file=arguments.history_file,
        console_output=not arguments.no_console,
        persist_history=not arguments.no_history,
        continue_on_publish_error=True,
        session_policy=session_policy,
        calendar_years=calendar_years,
        health_console_output=(
            not arguments.no_health_console
        ),
        health_history_file=(
            arguments.health_history_file
        ),
        persist_health_history=(
            not arguments.no_health_history
        ),
        health_status_file=(
            arguments.health_status_file
        ),
        health_status_indent=(
            arguments.health_status_indent
        ),
        create_health_status_parent_directories=(
            not arguments.no_health_status_parent_directories
        ),
    )


def publish_one_shot_result(
    *,
    application: RuntimeApplication,
    result: AnalysisCycleResult,
) -> None:
    application.publisher.publish(
        result
    )


def run_application(
    *,
    application,
    continuous: bool,
    max_cycles: int | None,
) -> int:
    if not isinstance(
        continuous,
        bool,
    ):
        raise TypeError(
            "continuous must be a bool."
        )

    if continuous:
        with RuntimeShutdownController(
            runner=application.continuous_runner,
        ):
            application.continuous_runner.run(
                max_cycles=max_cycles,
            )

        return 0

    result = application.one_shot_runner.run_once()

    publish_one_shot_result(
        application=application,
        result=result,
    )

    if result.status is AnalysisCycleStatus.FAILED:
        return 1

    return 0


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()

    arguments = parser.parse_args(
        argv
    )

    settings = load_settings()

    configure_logging(
        settings.log_level
    )

    logger = logging.getLogger(
        "imie.runtime"
    )

    try:
        application = build_application(
            settings=settings,
            arguments=arguments,
        )

        logger.info(
            "Starting IMIE runtime for %s on %s.",
            application.config.symbol,
            application.config.timeframe,
        )

        return run_application(
            application=application,
            continuous=arguments.continuous,
            max_cycles=arguments.max_cycles,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        parser.error(
            str(exc)
        )

    except Exception:
        logger.exception(
            "IMIE runtime terminated unexpectedly."
        )

        return 1

    return 1

    
if __name__ == "__main__":
    raise SystemExit(
        main()
    )