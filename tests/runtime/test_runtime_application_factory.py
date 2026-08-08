import json

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

import pytest

from imie.config.settings import (
    AppSettings,
)
from imie.runtime import (
    CompositeResultPublisher,
    ConsoleResultPublisher,
    ContinuousRuntimeRunner,
    InterruptibleSleeper,
    JsonLinesResultPublisher,
    MarketSessionState,
    RuntimeApplication,
    RuntimeApplicationFactory,
    RuntimeConfig,
    RuntimeHealthTracker,
    RuntimeRunner,
    SingleAnalysisCycle,
)
from imie.services import (
    MarketDataService,
)


def make_settings() -> AppSettings:
    return AppSettings(
        default_provider="mock",
    )


def test_factory_creates_complete_application(
    tmp_path: Path,
) -> None:
    config = RuntimeConfig(
        symbol="SPY",
        timeframe="2m",
        bar_limit=250,
    )

    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        config=config,
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    assert isinstance(
        application,
        RuntimeApplication,
    )

    assert application.config is config
    assert application.config.symbol == "SPY"

    assert application.cycle.config is config
    assert application.cycle.config.symbol == "SPY"

    assert isinstance(
        application.market_data,
        MarketDataService,
    )

    assert isinstance(
        application.cycle,
        SingleAnalysisCycle,
    )

    assert isinstance(
        application
        .continuous_runner
        .health_tracker,
        RuntimeHealthTracker,
    )

    assert isinstance(
        application.publisher,
        CompositeResultPublisher,
    )

    assert isinstance(
        application.one_shot_runner,
        RuntimeRunner,
    )

    assert (
        application.runtime_health
        is application
        .continuous_runner
        .health_tracker
        .current
    )

    assert application.completed_cycle_count == 0

    assert isinstance(
        application
        .continuous_runner
        .interruptible_sleeper,
        InterruptibleSleeper,
    )

    assert (
        application
        .continuous_runner
        .session_wake_planner
        is not None
    )

    assert isinstance(
        application.continuous_runner,
        ContinuousRuntimeRunner,
    )

    assert (
        application.cycle.market_data
        is application.market_data
    )

    assert (
        application.one_shot_runner.market_data
        is application.market_data
    )

    assert (
        application.continuous_runner.market_data
        is application.market_data
    )

    assert (
        application.one_shot_runner.cycle
        is application.cycle
    )

    assert (
        application.continuous_runner.cycle
        is application.cycle
    )


def test_factory_uses_default_runtime_config(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    assert application.config == RuntimeConfig()


def test_factory_builds_console_and_history_publishers(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    assert len(
        application.publisher.publishers
    ) == 2

    assert isinstance(
        application.publisher.publishers[0],
        ConsoleResultPublisher,
    )

    assert isinstance(
        application.publisher.publishers[1],
        JsonLinesResultPublisher,
    )


def test_console_only_configuration(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        history_file=(
            tmp_path
            / "unused.jsonl"
        ),
        console_output=True,
        persist_history=False,
    )

    assert len(
        application.publisher.publishers
    ) == 1

    assert isinstance(
        application.publisher.publishers[0],
        ConsoleResultPublisher,
    )


def test_history_only_configuration(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "cycles.jsonl"

    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        history_file=file_path,
        console_output=False,
        persist_history=True,
    )

    assert len(
        application.publisher.publishers
    ) == 1

    history_publisher = (
        application.publisher.publishers[0]
    )

    assert isinstance(
        history_publisher,
        JsonLinesResultPublisher,
    )

    assert history_publisher.file_path == file_path


def test_at_least_one_publisher_must_be_enabled() -> None:
    with pytest.raises(
        ValueError,
        match="At least one",
    ):
        RuntimeApplicationFactory.create(
            settings=make_settings(),
            console_output=False,
            persist_history=False,
        )


def test_settings_must_be_app_settings() -> None:
    with pytest.raises(
        TypeError,
        match="AppSettings",
    ):
        RuntimeApplicationFactory.create(
            settings=object(),  # type: ignore[arg-type]
        )


def test_config_must_be_runtime_config_or_none() -> None:
    with pytest.raises(
        TypeError,
        match="RuntimeConfig",
    ):
        RuntimeApplicationFactory.create(
            settings=make_settings(),
            config=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "console_output",
        "persist_history",
        "continue_on_publish_error",
    ],
)
def test_boolean_options_must_be_bool(
    field_name: str,
) -> None:
    arguments = {
        "settings": make_settings(),
        "console_output": True,
        "persist_history": True,
        "continue_on_publish_error": True,
    }

    arguments[field_name] = "yes"

    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        RuntimeApplicationFactory.create(
            **arguments,  # type: ignore[arg-type]
        )


def test_factory_does_not_connect_or_create_history_file(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "cycles.jsonl"

    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        history_file=file_path,
    )

    assert application is not None
    assert file_path.exists() is False

def test_factory_uses_nyse_exchange_calendar(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=AppSettings(
            default_provider="mock",
        ),
        config=RuntimeConfig(),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    clock = (
        application.one_shot_runner
        .cycle
        .market_session_clock
    )

    result = clock.evaluate(
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
        result.state
        is MarketSessionState.CLOSED
    )
    assert result.is_exchange_holiday is True

def test_factory_calendar_supports_2027(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=AppSettings(
            default_provider="mock",
        ),
        config=RuntimeConfig(),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    result = (
        application.one_shot_runner
        .cycle
        .market_session_clock
        .evaluate(
            datetime(
                2027,
                7,
                5,
                14,
                0,
                tzinfo=timezone.utc,
            )
        )
    )

    assert (
        result.state
        is MarketSessionState.CLOSED
    )
    assert result.is_exchange_holiday is True
    assert result.exchange_day is not None
    assert (
        result.exchange_day.holiday_name
        == "Independence Day Observed"
    )

def test_factory_accepts_selected_calendar_years(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=AppSettings(
            default_provider="mock",
        ),
        config=RuntimeConfig(),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
        calendar_years=(
            2028,
        ),
    )

    clock = (
        application.one_shot_runner
        .cycle
        .market_session_clock
    )

    result = clock.evaluate(
        datetime(
            2028,
            7,
            4,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert result.is_exchange_holiday is True


def test_factory_rejects_empty_calendar_years(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
            ),
            history_file=(
                tmp_path
                / "cycles.jsonl"
            ),
            calendar_years=(),
        )


def test_factory_rejects_non_tuple_calendar_years(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="tuple or None",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
            ),
            history_file=(
                tmp_path
                / "cycles.jsonl"
            ),
            calendar_years=[
                2026,
            ],  # type: ignore[arg-type]
        )


def test_factory_rejects_unsupported_calendar_year(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported NYSE calendar year",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
            ),
            history_file=(
                tmp_path
                / "cycles.jsonl"
            ),
            calendar_years=(
                2029,
            ),
        )


def test_factory_builds_health_publishers(
    tmp_path,
) -> None:
    health_file = (
        tmp_path
        / "health.jsonl"
    )

    application = (
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
            ),
            console_output=True,
            persist_history=False,
            health_console_output=False,
            persist_health_history=True,
            health_history_file=health_file,
        )
    )

    assert health_file.exists()

    lines = health_file.read_text(
        encoding="utf-8",
    ).splitlines()

    assert len(
        lines
    ) == 1

    assert len(
        application.publisher.publishers
    ) == 1

    assert isinstance(
        application.publisher.publishers[0],
        ConsoleResultPublisher,
    )


def test_factory_wires_health_status_file(
    tmp_path: Path,
) -> None:
    status_path = (
        tmp_path
        / "status"
        / "health.json"
    )

    application = (
        RuntimeApplicationFactory.create(
            settings=make_settings(),
            console_output=True,
            persist_history=False,
            health_console_output=False,
            persist_health_history=False,
            health_status_file=status_path,
        )
    )

    assert status_path.exists()

    payload = json.loads(
        status_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        type(
            application.continuous_runner
            .health_tracker
            .status_publisher
        ).__name__
        == "DashboardStatusFilePublisher"
    )

    assert payload["state"] == "CREATED"
    assert payload["completed_cycle_count"] == 0
    assert payload["symbol"] == "NVDA"
    assert payload["timeframe"] == "2m"
    assert payload["latest_cycle_status"] is None
    assert payload["latest_cycle_message"] is None
    assert payload["has_cycle"] is False
    assert payload["cycle_failed"] is False

    assert (
        application.continuous_runner
        .health_tracker
        .status_publisher
        is not None
    )