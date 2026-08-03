from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from imie.config.settings import (
    AppSettings,
)
from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    RuntimeApplicationFactory,
    RuntimeConfig,
    SUPPORTED_NYSE_CALENDAR_YEARS,
)
from imie.runtime_cli import (
    build_application,
    build_parser,
    build_runtime_config,
    build_session_policy,
    main,
    publish_one_shot_result,
    resolve_calendar_years,
    resolve_settings,
    run_application,
)
from imie.providers.mock_provider import MockProvider
from imie.providers.provider_factory import ProviderFactory


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


def make_arguments(
    **overrides,
) -> Namespace:
    values = {
        "symbol": "NVDA",
        "provider": None,
        "timeframe": "2m",
        "bar_limit": 500,
        "poll_seconds": 5.0,
        "closed_poll_seconds": 300.0,
        "heartbeat_seconds": 60.0,
        "completion_delay": 3.0,
        "continuous": False,
        "max_cycles": None,
        "history_file": Path(
            "runtime/history/imie_cycles.jsonl"
        ),
        "no_console": False,
        "no_history": False,
        "allow_after_hours": False,
        "allow_closed": False,
        "disable_premarket": False,
        "calendar_years": None,
        "health_history_file": Path(
            "runtime/history/imie_health.jsonl"
        ),
        "no_health_console": False,
        "no_health_history": False,
        "health_status_file": None,
        "health_status_indent": 2,
        "no_health_status_parent_directories": False,
    }

    values.update(
        overrides
    )

    return Namespace(
        **values
    )


def make_result(
    *,
    failed: bool = False,
) -> AnalysisCycleResult:
    if failed:
        return AnalysisCycleResult(
            status=AnalysisCycleStatus.FAILED,
            symbol="NVDA",
            timeframe="2m",
            started_at=CHECKED_AT,
            completed_at=CHECKED_AT,
            message="Provider unavailable.",
            error_type="RuntimeError",
        )

    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus
            .SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="No new completed bar.",
    )


def test_parser_defaults() -> None:
    parser = build_parser()

    arguments = parser.parse_args(
        []
    )

    assert arguments.symbol == "NVDA"
    assert arguments.timeframe == "2m"
    assert arguments.bar_limit == 500
    assert arguments.poll_seconds == 5.0
    assert arguments.completion_delay == 3.0
    assert arguments.closed_poll_seconds == 300.0
    assert arguments.continuous is False
    assert arguments.max_cycles is None
    assert arguments.no_console is False
    assert arguments.no_history is False
    assert arguments.provider is None
    assert arguments.allow_after_hours is False
    assert arguments.allow_closed is False
    assert arguments.disable_premarket is False
    assert arguments.calendar_years is None
    assert arguments.heartbeat_seconds == 60.0
    assert arguments.health_status_file is None
    assert arguments.health_status_indent == 2
    assert (
        arguments.no_health_status_parent_directories
        is False
    )
    

def test_parser_accepts_runtime_options() -> None:
    parser = build_parser()

    arguments = parser.parse_args(
        [
            "--symbol",
            "spy",
            "--timeframe",
            "5m",
            "--bar-limit",
            "250",
            "--poll-seconds",
            "7.5",
            "--completion-delay",
            "2",
            "--continuous",
            "--max-cycles",
            "3",
            "--history-file",
            "output/cycles.jsonl",
            "--no-console",
            "--provider",
            "alpaca",
            "--closed-poll-seconds",
            "180",
            "--heartbeat-seconds",
            "30",
            "--health-status-file",
            "runtime/health.json",
            "--health-status-indent",
            "4",
            "--no-health-status-parent-directories",
        ]
    )

    assert arguments.symbol == "spy"
    assert arguments.timeframe == "5m"
    assert arguments.bar_limit == 250
    assert arguments.poll_seconds == 7.5
    assert arguments.completion_delay == 2.0
    assert arguments.continuous is True
    assert arguments.max_cycles == 3
    assert arguments.history_file == Path(
        "output/cycles.jsonl"
    )
    assert arguments.no_console is True
    assert arguments.provider == "alpaca"
    assert arguments.closed_poll_seconds == 180.0
    assert arguments.heartbeat_seconds == 30.0
    assert arguments.health_status_file == Path(
        "runtime/health.json"
    )
    assert arguments.health_status_indent == 4
    assert (
        arguments.no_health_status_parent_directories
        is True
    )


def test_build_runtime_config() -> None:
    config = build_runtime_config(
        make_arguments(
            symbol=" spy ",
            timeframe="5m",
            bar_limit=250,
            poll_seconds=7.5,
            closed_poll_seconds=180.0,
            completion_delay=2.0,
            heartbeat_seconds=30.0,
        )
    )

    assert config == RuntimeConfig(
        symbol="SPY",
        timeframe="5m",
        bar_limit=250,
        polling_interval_seconds=7.5,
        closed_session_polling_interval_seconds=180.0,
        completion_delay_seconds=2.0,
        heartbeat_interval_seconds=30.0,
    )

def test_parser_accepts_session_overrides() -> None:
    arguments = build_parser().parse_args(
        [
            "--allow-after-hours",
            "--allow-closed",
            "--disable-premarket",
        ]
    )

    assert arguments.allow_after_hours is True
    assert arguments.allow_closed is True
    assert arguments.disable_premarket is True


def test_build_application(
    tmp_path: Path,
) -> None:
    application = build_application(
        settings=AppSettings(
            default_provider="mock",
        ),
        arguments=make_arguments(
            history_file=(
                tmp_path
                / "cycles.jsonl"
            ),
        ),
    )

    assert application.config.symbol == "NVDA"
    assert application.config.timeframe == "2m"
    assert application.config.bar_limit == 500


def test_build_application_requires_publisher() -> None:
    with pytest.raises(
        ValueError,
        match="At least one",
    ):
        build_application(
            settings=AppSettings(
                default_provider="mock",
            ),
            arguments=make_arguments(
                no_console=True,
                no_history=True,
            ),
        )

def test_build_session_policy_uses_defaults() -> None:
    policy = build_session_policy(
        make_arguments()
    )

    assert (
        policy.config.allow_premarket
        is True
    )
    assert (
        policy.config.allow_regular_session
        is True
    )
    assert (
        policy.config.allow_after_hours
        is False
    )
    assert (
        policy.config.allow_closed
        is False
    )


def test_build_session_policy_applies_overrides() -> None:
    policy = build_session_policy(
        make_arguments(
            allow_after_hours=True,
            allow_closed=True,
            disable_premarket=True,
        )
    )

    assert (
        policy.config.allow_premarket
        is False
    )
    assert (
        policy.config.allow_regular_session
        is True
    )
    assert (
        policy.config.allow_after_hours
        is True
    )
    assert (
        policy.config.allow_closed
        is True
    )


def test_build_session_policy_requires_namespace() -> None:
    with pytest.raises(
        TypeError,
        match="argparse.Namespace",
    ):
        build_session_policy(
            object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "allow_after_hours",
        "allow_closed",
        "disable_premarket",
    ],
)
def test_build_session_policy_requires_bool_flags(
    field_name: str,
) -> None:
    arguments = make_arguments()

    setattr(
        arguments,
        field_name,
        "yes",
    )

    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        build_session_policy(
            arguments
        )


class FakePublisher:
    def __init__(self) -> None:
        self.results: list[
            AnalysisCycleResult
        ] = []

    def publish(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.results.append(
            result
        )


class FakeOneShotRunner:
    def __init__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.result = result
        self.calls = 0

    def run_once(
        self,
    ) -> AnalysisCycleResult:
        self.calls += 1
        return self.result


class FakeContinuousRunner:
    def __init__(self) -> None:
        self.calls: list[
            int | None
        ] = []
        self.stop_calls = 0

    def run(
        self,
        *,
        max_cycles: int | None = None,
    ) -> tuple[AnalysisCycleResult, ...]:
        self.calls.append(
            max_cycles
        )
        return ()

    def request_stop(
        self,
    ) -> None:
        self.stop_calls += 1


class FakeApplication:
    def __init__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publisher = FakePublisher()
        self.one_shot_runner = (
            FakeOneShotRunner(
                result
            )
        )
        self.continuous_runner = (
            FakeContinuousRunner()
        )


def test_run_application_one_shot_publishes_result() -> None:
    result = make_result()

    application = FakeApplication(
        result
    )

    exit_code = run_application(
        application=application,  # type: ignore[arg-type]
        continuous=False,
        max_cycles=None,
    )

    assert exit_code == 0
    assert (
        application.one_shot_runner.calls
        == 1
    )
    assert application.publisher.results == [
        result,
    ]
    assert (
        application.continuous_runner.calls
        == []
    )


def test_run_application_returns_one_for_failed_cycle() -> None:
    result = make_result(
        failed=True
    )

    application = FakeApplication(
        result
    )

    exit_code = run_application(
        application=application,  # type: ignore[arg-type]
        continuous=False,
        max_cycles=None,
    )

    assert exit_code == 1
    assert application.publisher.results == [
        result,
    ]


def test_run_application_continuous_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = FakeApplication(
        make_result()
    )

    monkeypatch.setattr(
        "imie.runtime_cli.RuntimeShutdownController",
        RecordingShutdownController,
    )

    exit_code = run_application(
        application=application,  # type: ignore[arg-type]
        continuous=True,
        max_cycles=3,
    )

    assert exit_code == 0

    assert (
        application.continuous_runner.calls
        == [
            3,
        ]
    )

    assert (
        application.one_shot_runner.calls
        == 0
    )

    assert application.publisher.results == []


def test_resolve_settings_preserves_default_provider() -> None:
    settings = AppSettings(
        default_provider="mock",
    )

    resolved = resolve_settings(
        settings=settings,
        arguments=make_arguments(
            provider=None,
        ),
    )

    assert resolved is settings
    assert resolved.default_provider == "mock"


def test_resolve_settings_overrides_provider() -> None:
    settings = AppSettings(
        default_provider="mock",
    )

    resolved = resolve_settings(
        settings=settings,
        arguments=make_arguments(
            provider="alpaca",
        ),
    )

    assert resolved is not settings
    assert resolved.default_provider == "alpaca"
    assert settings.default_provider == "mock"


def test_resolve_settings_normalizes_provider() -> None:
    resolved = resolve_settings(
        settings=AppSettings(
            default_provider="mock",
        ),
        arguments=make_arguments(
            provider=" ALPACA ",
        ),
    )

    assert resolved.default_provider == "alpaca"


def test_resolve_settings_rejects_invalid_provider() -> None:
    with pytest.raises(
        ValueError,
        match="provider",
    ):
        resolve_settings(
            settings=AppSettings(),
            arguments=make_arguments(
                provider="invalid",
            ),
        )


def test_resolve_settings_requires_app_settings() -> None:
    with pytest.raises(
        TypeError,
        match="AppSettings",
    ):
        resolve_settings(
            settings=object(),  # type: ignore[arg-type]
            arguments=make_arguments(),
        )

def test_build_application_uses_provider_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested_providers: list[str] = []

    def recording_create(
        provider_name: str,
    ) -> MockProvider:
        requested_providers.append(provider_name)
        return MockProvider()

    monkeypatch.setattr(
        ProviderFactory,
        "create",
        staticmethod(recording_create),
    )

    arguments = make_arguments(
        provider="alpaca",
        allow_after_hours=True,
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    application = build_application(
        settings=AppSettings(
            default_provider="mock",
        ),
        arguments=arguments,
    )

    assert requested_providers == [
        "alpaca",
    ]

    assert (
        application.one_shot_runner
        .cycle
        .session_policy
        .config
        .allow_after_hours
        is True
    )

def test_parser_accepts_calendar_years() -> None:
    arguments = build_parser().parse_args(
        [
            "--calendar-years",
            "2026",
            "2028",
        ]
    )

    assert arguments.calendar_years == [
        2026,
        2028,
    ]

def test_parser_rejects_unsupported_calendar_year() -> None:
    with pytest.raises(
        SystemExit,
    ):
        build_parser().parse_args(
            [
                "--calendar-years",
                "2029",
            ]
        )

def test_resolve_calendar_years_uses_defaults() -> None:
    result = resolve_calendar_years(
        make_arguments()
    )

    assert (
        result
        == SUPPORTED_NYSE_CALENDAR_YEARS
    )


def test_resolve_calendar_years_uses_selection() -> None:
    result = resolve_calendar_years(
        make_arguments(
            calendar_years=[
                2026,
                2028,
            ],
        )
    )

    assert result == (
        2026,
        2028,
    )


def test_resolve_calendar_years_deduplicates() -> None:
    result = resolve_calendar_years(
        make_arguments(
            calendar_years=[
                2027,
                2027,
                2026,
            ],
        )
    )

    assert result == (
        2027,
        2026,
    )


def test_resolve_calendar_years_requires_namespace() -> None:
    with pytest.raises(
        TypeError,
        match="argparse.Namespace",
    ):
        resolve_calendar_years(
            object(),  # type: ignore[arg-type]
        )


def test_resolve_calendar_years_requires_list() -> None:
    with pytest.raises(
        TypeError,
        match="list or None",
    ):
        resolve_calendar_years(
            make_arguments(
                calendar_years=(
                    2026,
                    2027,
                ),
            )
        )


def test_resolve_calendar_years_rejects_empty_list() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        resolve_calendar_years(
            make_arguments(
                calendar_years=[],
            )
        )


def test_resolve_calendar_years_rejects_non_integer() -> None:
    with pytest.raises(
        TypeError,
        match="only integers",
    ):
        resolve_calendar_years(
            make_arguments(
                calendar_years=[
                    "2026",
                ],
            )
        )


def test_resolve_calendar_years_rejects_unsupported_year() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported NYSE calendar year",
    ):
        resolve_calendar_years(
            make_arguments(
                calendar_years=[
                    2029,
                ],
            )
        )

def test_build_application_uses_selected_calendar_years(
    tmp_path: Path,
) -> None:
    application = build_application(
        settings=AppSettings(
            default_provider="mock",
        ),
        arguments=make_arguments(
            calendar_years=[
                2027,
            ],
            history_file=(
                tmp_path
                / "cycles.jsonl"
            ),
        ),
    )

    clock = (
        application.one_shot_runner
        .cycle
        .market_session_clock
    )

    selected_year_result = clock.evaluate(
        datetime(
            2027,
            7,
            5,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    excluded_year_result = clock.evaluate(
        datetime(
            2026,
            7,
            3,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert (
        selected_year_result.is_exchange_holiday
        is True
    )

    assert (
        excluded_year_result.is_exchange_holiday
        is False
    )

class RecordingShutdownController:
    instances: list[
        "RecordingShutdownController"
    ] = []

    def __init__(
        self,
        *,
        runner,
    ) -> None:
        self.runner = runner
        self.enter_calls = 0
        self.exit_calls = 0

        self.__class__.instances.append(
            self
        )

    def __enter__(
        self,
    ):
        self.enter_calls += 1
        return self

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ) -> bool:
        del exception_type
        del exception
        del traceback

        self.exit_calls += 1
        return False


@pytest.fixture(
    autouse=True,
)
def clear_recording_shutdown_controllers() -> None:
    RecordingShutdownController.instances.clear()


def test_run_application_one_shot_does_not_install_shutdown_controller(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = FakeApplication(
        make_result()
    )

    def fail_if_created(
        *,
        runner,
    ):
        del runner

        raise AssertionError(
            "Shutdown controller should not be created "
            "for one-shot execution."
        )

    monkeypatch.setattr(
        "imie.runtime_cli.RuntimeShutdownController",
        fail_if_created,
    )

    exit_code = run_application(
        application=application,  # type: ignore[arg-type]
        continuous=False,
        max_cycles=None,
    )

    assert exit_code == 0
    assert application.one_shot_runner.calls == 1
    assert application.continuous_runner.calls == []


def test_run_application_continuous_installs_shutdown_controller(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    RecordingShutdownController.instances.clear()

    application = FakeApplication(
        make_result()
    )

    monkeypatch.setattr(
        "imie.runtime_cli.RuntimeShutdownController",
        RecordingShutdownController,
    )

    exit_code = run_application(
        application=application,  # type: ignore[arg-type]
        continuous=True,
        max_cycles=3,
    )

    assert exit_code == 0
    assert application.one_shot_runner.calls == 0
    assert application.continuous_runner.calls == [
        3,
    ]

    assert len(
        RecordingShutdownController.instances
    ) == 1

    controller = (
        RecordingShutdownController.instances[0]
    )

    assert (
        controller.runner
        is application.continuous_runner
    )
    assert controller.enter_calls == 1
    assert controller.exit_calls == 1

class RaisingContinuousRunner:
    def __init__(
        self,
    ) -> None:
        self.calls: list[
            int | None
        ] = []

    def run(
        self,
        *,
        max_cycles: int | None = None,
    ) -> tuple[AnalysisCycleResult, ...]:
        self.calls.append(
            max_cycles
        )

        raise RuntimeError(
            "Continuous runtime failed."
        )

    def request_stop(
        self,
    ) -> None:
        pass


def test_run_application_continuous_restores_controller_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    RecordingShutdownController.instances.clear()

    application = FakeApplication(
        make_result()
    )

    application.continuous_runner = (
        RaisingContinuousRunner()
    )

    monkeypatch.setattr(
        "imie.runtime_cli.RuntimeShutdownController",
        RecordingShutdownController,
    )

    with pytest.raises(
        RuntimeError,
        match="Continuous runtime failed",
    ):
        run_application(
            application=application,  # type: ignore[arg-type]
            continuous=True,
            max_cycles=2,
        )

    assert len(
        RecordingShutdownController.instances
    ) == 1

    controller = (
        RecordingShutdownController.instances[0]
    )

    assert controller.enter_calls == 1
    assert controller.exit_calls == 1

@pytest.mark.parametrize(
    "value",
    [
        1,
        0,
        "true",
        None,
    ],
)
def test_run_application_continuous_must_be_bool(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="continuous",
    ):
        run_application(
            application=FakeApplication(
                make_result()
            ),  # type: ignore[arg-type]
            continuous=value,  # type: ignore[arg-type]
            max_cycles=None,
        )

def test_build_application_passes_health_status_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = make_arguments(
        health_status_file=Path(
            "runtime/health.json"
        ),
        health_status_indent=4,
        no_health_status_parent_directories=True,
    )

    captured: dict[
        str,
        object,
    ] = {}

    def fake_create(
        **kwargs: object,
    ) -> object:
        captured.update(
            kwargs
        )

        return object()

    monkeypatch.setattr(
        RuntimeApplicationFactory,
        "create",
        fake_create,
    )

    application = build_application(
        settings=AppSettings(
            default_provider="mock",
        ),
        arguments=arguments,
    )

    assert application is not None

    assert captured[
        "health_status_file"
    ] == Path(
        "runtime/health.json"
    )

    assert captured[
        "health_status_indent"
    ] == 4

    assert (
        captured[
            "create_health_status_parent_directories"
        ]
        is False
    )


