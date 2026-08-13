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
    MultiSymbolRuntimeApplication,
)
from imie.services import (
    MarketDataService,
)
from imie.execution import (
    AlpacaPaperExecutionAdapter,
    AlpacaPaperFillActivitySource,
    BrokerOrderQueryPort,
    MockBrokerExecutionAdapter,
)
from imie.runtime.runtime_application_factory import (
    _build_symbol_cycles,
)
from imie.runtime.runtime_symbol_universe import (
    RuntimeSymbolUniverse,
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
    assert application.cycle.broker_execution_port is None


def test_factory_injects_mock_broker_only_when_enabled(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        config=RuntimeConfig(
            execution_mode="mock",
        ),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    assert isinstance(
        application.cycle.broker_execution_port,
        MockBrokerExecutionAdapter,
    )
    assert application.cycle.protected_execution_port is None


def test_factory_injects_protected_alpaca_paper_port(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=AppSettings(
            default_provider="mock",
            alpaca_api_key="paper-key",
            alpaca_secret_key="paper-secret",
            alpaca_paper=True,
        ),
        config=RuntimeConfig(
            execution_mode="alpaca-paper",
            paper_execution_confirmed=True,
        ),
        history_file=tmp_path / "cycles.jsonl",
    )

    assert application.cycle.broker_execution_port is None
    assert isinstance(
        application.cycle.protected_execution_port,
        AlpacaPaperExecutionAdapter,
    )
    assert isinstance(
        application.cycle.protected_execution_port,
        BrokerOrderQueryPort,
    )
    assert isinstance(
        application.cycle.protected_execution_port._fill_activity_source,
        AlpacaPaperFillActivitySource,
    )


def test_factory_rejects_unconfirmed_alpaca_paper_mode(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="--confirm-paper-execution",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
                alpaca_api_key="paper-key",
                alpaca_secret_key="paper-secret",
                alpaca_paper=True,
            ),
            config=RuntimeConfig(
                execution_mode="alpaca-paper",
            ),
            history_file=tmp_path / "cycles.jsonl",
        )


def test_factory_rejects_alpaca_paper_mode_when_paper_is_false(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="ALPACA_PAPER=true",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
                alpaca_api_key="paper-key",
                alpaca_secret_key="paper-secret",
                alpaca_paper=False,
            ),
            config=RuntimeConfig(
                execution_mode="alpaca-paper",
                paper_execution_confirmed=True,
            ),
            history_file=tmp_path / "cycles.jsonl",
        )


@pytest.mark.parametrize(
    ("api_key", "secret_key"),
    [
        ("", "paper-secret"),
        ("paper-key", ""),
        (" ", "paper-secret"),
    ],
)
def test_factory_rejects_alpaca_paper_mode_without_credentials(
    tmp_path: Path,
    api_key: str,
    secret_key: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="ALPACA_API_KEY.*ALPACA_SECRET_KEY",
    ):
        RuntimeApplicationFactory.create(
            settings=AppSettings(
                default_provider="mock",
                alpaca_api_key=api_key,
                alpaca_secret_key=secret_key,
                alpaca_paper=True,
            ),
            config=RuntimeConfig(
                execution_mode="alpaca-paper",
                paper_execution_confirmed=True,
            ),
            history_file=tmp_path / "cycles.jsonl",
        )


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

def test_symbol_cycles_share_market_data_and_session_dependencies(
    tmp_path: Path,
) -> None:
    application = RuntimeApplicationFactory.create(
        settings=make_settings(),
        config=RuntimeConfig(
            symbol="NVDA",
            timeframe="2m",
        ),
        history_file=(
            tmp_path
            / "cycles.jsonl"
        ),
    )

    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    cycles = _build_symbol_cycles(
        universe=universe,
        base_config=application.config,
        market_data=application.market_data,
        market_session_clock=(
            application.cycle.market_session_clock
        ),
        session_policy=(
            application.cycle.session_policy
        ),
    )

    assert tuple(
        cycle.config.symbol
        for cycle in cycles
    ) == (
        "NVDA",
        "AMD",
        "SPY",
    )

    for cycle in cycles:
        assert cycle.market_data is application.market_data
        assert (
            cycle.market_session_clock
            is application.cycle.market_session_clock
        )
        assert (
            cycle.session_policy
            is application.cycle.session_policy
        )

def test_factory_creates_multi_symbol_application() -> None:
    universe = RuntimeSymbolUniverse(
        symbols=(
            "NVDA",
            "AMD",
            "SPY",
        )
    )

    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=universe,
        )
    )

    assert isinstance(
        application,
        MultiSymbolRuntimeApplication,
    )

    assert application.universe is universe

    assert tuple(
        cycle.config.symbol
        for cycle in application.cycles
    ) == (
        "NVDA",
        "AMD",
        "SPY",
    )

    assert (
        application.cycle_runner.universe
        is application.universe
    )

    assert (
        application.cycle_runner.cycles
        == application.cycles
    )

    assert (
        application.one_shot_runner.runner
        is application.cycle_runner
    )

    assert (
        application.one_shot_runner.market_data
        is application.market_data
    )

    assert all(
        cycle.broker_execution_port is None
        for cycle in application.cycles
    )


def test_multi_symbol_factory_injects_shared_mock_broker() -> None:
    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=RuntimeSymbolUniverse(
                symbols=(
                    "NVDA",
                    "AMD",
                )
            ),
            config=RuntimeConfig(
                execution_mode="mock",
            ),
        )
    )

    broker_execution_ports = tuple(
        cycle.broker_execution_port
        for cycle in application.cycles
    )

    assert isinstance(
        broker_execution_ports[0],
        MockBrokerExecutionAdapter,
    )
    assert all(
        port is broker_execution_ports[0]
        for port in broker_execution_ports
    )
    assert all(
        cycle.protected_execution_port is None
        for cycle in application.cycles
    )


def test_multi_symbol_factory_injects_shared_alpaca_paper_port() -> None:
    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=AppSettings(
                default_provider="mock",
                alpaca_api_key="paper-key",
                alpaca_secret_key="paper-secret",
                alpaca_paper=True,
            ),
            universe=RuntimeSymbolUniverse(
                symbols=(
                    "NVDA",
                    "AMD",
                )
            ),
            config=RuntimeConfig(
                execution_mode="alpaca-paper",
                paper_execution_confirmed=True,
            ),
        )
    )

    protected_execution_ports = tuple(
        cycle.protected_execution_port
        for cycle in application.cycles
    )

    assert all(
        cycle.broker_execution_port is None
        for cycle in application.cycles
    )
    assert isinstance(
        protected_execution_ports[0],
        AlpacaPaperExecutionAdapter,
    )
    assert isinstance(
        protected_execution_ports[0],
        BrokerOrderQueryPort,
    )
    assert isinstance(
        protected_execution_ports[0]._fill_activity_source,
        AlpacaPaperFillActivitySource,
    )
    assert all(
        port is protected_execution_ports[0]
        for port in protected_execution_ports
    )


def test_multi_symbol_factory_shares_market_data() -> None:
    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=RuntimeSymbolUniverse(
                symbols=(
                    "NVDA",
                    "AMD",
                    "SPY",
                )
            ),
        )
    )

    for cycle in application.cycles:
        assert (
            cycle.market_data
            is application.market_data
        )


def test_multi_symbol_factory_preserves_base_config() -> None:
    config = RuntimeConfig(
        symbol="NVDA",
        timeframe="5m",
        bar_limit=250,
    )

    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=RuntimeSymbolUniverse(
                symbols=(
                    "NVDA",
                    "AMD",
                )
            ),
            config=config,
        )
    )

    assert tuple(
        cycle.config.timeframe
        for cycle in application.cycles
    ) == (
        "5m",
        "5m",
    )

    assert tuple(
        cycle.config.bar_limit
        for cycle in application.cycles
    ) == (
        250,
        250,
    )


def test_multi_symbol_factory_uses_first_symbol_as_default_config() -> None:
    application = (
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=RuntimeSymbolUniverse(
                symbols=(
                    "AMD",
                    "SPY",
                )
            ),
        )
    )

    assert tuple(
        cycle.config.symbol
        for cycle in application.cycles
    ) == (
        "AMD",
        "SPY",
    )


def test_multi_symbol_factory_requires_symbol_universe() -> None:
    with pytest.raises(
        TypeError,
        match="RuntimeSymbolUniverse",
    ):
        RuntimeApplicationFactory.create_multi_symbol(
            settings=make_settings(),
            universe=object(),  # type: ignore[arg-type]
        )
