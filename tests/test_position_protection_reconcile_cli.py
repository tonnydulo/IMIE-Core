from datetime import datetime, timezone
from pathlib import Path

import pytest

import imie.position_protection_reconcile_cli as cli
from imie.config.settings import AppSettings
from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    PositionProtectionReconciliationResult,
)


NOW = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)


def settings(*, paper=True, key="key", secret="secret"):
    return AppSettings(
        alpaca_api_key=key,
        alpaca_secret_key=secret,
        alpaca_paper=paper,
    )


def result(state="active"):
    snapshot = BrokerOrderSnapshot(
        broker="alpaca-paper",
        broker_order_id="target-1",
        symbol="NVDA",
        side="sell",
        order_type="limit",
        status=BrokerOrderStatus.ACCEPTED,
        requested_quantity=5,
        filled_quantity=0,
        remaining_quantity=5,
        last_updated_at=NOW,
    )
    return PositionProtectionReconciliationResult(
        broker="alpaca-paper",
        symbol="NVDA",
        state=state,
        requested_quantity=5,
        active_quantity=5 if state == "active" else 0,
        triggered_quantity=5 if state == "triggered" else 0,
        reconciled=state != "indeterminate",
        snapshots=(snapshot,),
    )


def test_parser_defaults():
    arguments = cli.build_parser().parse_args(["NVDA"])

    assert arguments.position_store == Path("runtime/execution/positions.json")
    assert arguments.protection_store == Path(
        "runtime/execution/position_protections.json"
    )
    assert arguments.reconciliation_store == Path(
        "runtime/execution/position_protection_reconciliations.json"
    )
    assert arguments.output_format == "console"


def test_build_service_requires_explicit_paper_mode():
    with pytest.raises(ValueError, match="ALPACA_PAPER=true"):
        cli.build_service(
            settings=settings(paper=False),
            position_store_path=Path("positions.json"),
            protection_store_path=Path("protections.json"),
            reconciliation_store_path=Path("reconciliations.json"),
        )


@pytest.mark.parametrize("value", [settings(key=""), settings(secret="")])
def test_build_service_requires_credentials(value):
    with pytest.raises(ValueError, match="ALPACA_API_KEY"):
        cli.build_service(
            settings=value,
            position_store_path=Path("positions.json"),
            protection_store_path=Path("protections.json"),
            reconciliation_store_path=Path("reconciliations.json"),
        )


@pytest.mark.parametrize("state, exit_code", [("active", 0), ("triggered", 0), ("degraded", 2), ("terminal_unprotected", 2), ("indeterminate", 2)])
def test_main_reconciles_once_and_maps_state_to_exit_code(
    monkeypatch, state, exit_code
):
    calls = []

    class Service:
        def reconcile(self, **kwargs):
            calls.append(kwargs)
            return result(state)

    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_result", lambda **kwargs: None)

    assert cli.main(["nvda"]) == exit_code
    assert calls == [{"broker": "alpaca-paper", "symbol": "nvda"}]


def test_main_returns_one_on_query_failure(monkeypatch):
    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(
        cli,
        "build_service",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("failed")),
    )

    assert cli.main(["NVDA"]) == 1


def test_publish_result_renders_json(capsys):
    cli.publish_result(result=result(), output_format="json", json_indent=0)

    output = capsys.readouterr().out
    assert '"state": "active"' in output
    assert '"broker_order_id": "target-1"' in output


def test_cli_import_has_no_broker_client_or_analysis_runtime():
    assert "AlpacaPaperExecutionAdapter" not in cli.__dict__
    assert "RuntimeApplicationFactory" not in cli.__dict__
