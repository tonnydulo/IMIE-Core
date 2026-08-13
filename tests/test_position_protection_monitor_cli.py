from datetime import datetime, timezone
from pathlib import Path

import pytest

import imie.position_protection_monitor_cli as cli
from imie.models import PositionProtectionMonitoringAssessment


NOW = datetime(2026, 8, 14, 4, 0, tzinfo=timezone.utc)


def assessment(*, healthy=True, state=None):
    return PositionProtectionMonitoringAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        state=state or ("fresh_healthy" if healthy else "stale"),
        checked_at=NOW,
        observed_at=NOW,
        observation_age_seconds=0.0,
        maximum_age_seconds=30.0,
        reconciliation_state="active",
        healthy=healthy,
        action_required=not healthy,
        reason="Assessment complete.",
    )


def test_parser_defaults_to_thirty_second_local_check():
    arguments = cli.build_parser().parse_args(["NVDA"])

    assert arguments.position_store == Path("runtime/execution/positions.json")
    assert arguments.reconciliation_store == Path(
        "runtime/execution/position_protection_reconciliations.json"
    )
    assert arguments.maximum_age_seconds == 30.0


@pytest.mark.parametrize("healthy, exit_code", [(True, 0), (False, 2)])
def test_main_maps_health_to_exit_code(monkeypatch, healthy, exit_code):
    calls = []

    class Service:
        def assess(self, **kwargs):
            calls.append(kwargs)
            return assessment(healthy=healthy)

    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_assessment", lambda **kwargs: None)

    assert cli.main(["nvda", "--maximum-age-seconds", "15"]) == exit_code
    assert calls == [{"broker": "alpaca-paper", "symbol": "nvda"}]


def test_invalid_maximum_age_returns_failure(monkeypatch):
    monkeypatch.setattr(
        cli,
        "build_service",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("positive")),
    )

    assert cli.main(["NVDA", "--maximum-age-seconds", "0"]) == 1


def test_publish_assessment_renders_json(capsys):
    cli.publish_assessment(
        assessment=assessment(), output_format="json", json_indent=0
    )

    output = capsys.readouterr().out
    assert '"state": "fresh_healthy"' in output
    assert '"healthy": true' in output


def test_cli_import_has_no_broker_adapter_or_analysis_runtime():
    assert "AlpacaPaperExecutionAdapter" not in cli.__dict__
    assert "RuntimeApplicationFactory" not in cli.__dict__
