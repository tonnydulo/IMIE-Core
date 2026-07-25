from imie.runtime import (
    RuntimeApplication,
    RuntimeHealthState,
    RuntimeHealthSummary,
)
from imie.runtime.runtime_application_factory import (
    RuntimeApplicationFactory,
)
from imie.config.settings import (
    AppSettings,
)
import json


def make_application() -> RuntimeApplication:
    return RuntimeApplicationFactory.create(
        settings=AppSettings(
            default_provider="mock",
        ),
        console_output=True,
        persist_history=False,
    )


def test_application_exposes_runtime_health() -> None:
    application = make_application()

    assert (
        application.runtime_health.state
        is RuntimeHealthState.CREATED
    )

    assert (
        application.runtime_health
        is application
        .continuous_runner
        .health_tracker
        .current
    )


def test_application_exposes_runtime_health_history() -> None:
    application = make_application()

    assert (
        application.runtime_health_history
        == application
        .continuous_runner
        .health_tracker
        .history
    )

    assert len(
        application.runtime_health_history
    ) == 1


def test_application_exposes_completed_cycle_count() -> None:
    application = make_application()

    assert application.completed_cycle_count == 0


def test_application_exposes_health_summary() -> None:
    application = make_application()

    summary = application.health_summary

    assert isinstance(
        summary,
        RuntimeHealthSummary,
    )

    assert (
        summary.state
        is RuntimeHealthState.CREATED
    )

    assert summary.completed_cycle_count == 0


def test_application_exposes_health_status() -> None:
    application = make_application()

    status = application.health_status

    assert status["state"] == "CREATED"
    assert status["completed_cycle_count"] == 0
    assert status["running"] is False
    assert status["terminal"] is False
    assert status["failed"] is False


def test_application_exposes_health_status_json() -> None:
    application = make_application()

    payload = application.health_status_json()

    decoded = json.loads(
        payload
    )

    assert decoded["state"] == "CREATED"
    assert decoded["completed_cycle_count"] == 0


def test_application_health_status_json_supports_indent() -> None:
    application = make_application()

    payload = application.health_status_json(
        indent=2
    )

    decoded = json.loads(
        payload
    )

    assert "\n" in payload
    assert decoded["state"] == "CREATED"
    assert decoded["completed_cycle_count"] == 0

    