from datetime import datetime, timezone
from pathlib import Path

import pytest

from imie.config.settings import AppSettings
from imie.models import ExecutionPosition, PositionDirection
import imie.position_reconcile_cli as cli


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def position():
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=200.0,
        market_price=201.0,
        unrealized_pnl=40.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def test_parser_defaults():
    arguments = cli.build_parser().parse_args(["order-123", "NVDA"])

    assert arguments.position_store == Path("runtime/execution/positions.json")
    assert arguments.market_price is None
    assert arguments.output_format == "console"


def test_build_service_requires_explicit_paper_mode():
    with pytest.raises(ValueError, match="ALPACA_PAPER=true"):
        cli.build_service(
            settings=AppSettings(
                alpaca_api_key="key", alpaca_secret_key="secret", alpaca_paper=False
            ),
            position_store_path=Path("positions.json"),
        )


def test_build_service_wires_paper_query_and_position_store():
    service = cli.build_service(
        settings=AppSettings(
            alpaca_api_key="key", alpaca_secret_key="secret", alpaca_paper=True
        ),
        position_store_path=Path("custom-positions.json"),
    )

    assert service._query_port.broker_name == "alpaca-paper"
    assert service._query_port._intent_store is None
    assert service._position_store.path == Path("custom-positions.json")


def test_main_explicitly_reconciles_once(monkeypatch):
    calls = []

    class Service:
        def reconcile_order_position(self, **kwargs):
            calls.append(kwargs)
            return position()

    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_result", lambda **kwargs: None)

    assert cli.main(["order-123", "nvda", "--market-price", "201"]) == 0
    assert calls == [{
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "symbol": "nvda",
        "market_price": 201.0,
    }]


def test_main_returns_one_on_failure(monkeypatch):
    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(
        cli,
        "build_service",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("failed")),
    )

    assert cli.main(["order-123", "NVDA"]) == 1


def test_publish_result_renders_json(capsys):
    cli.publish_result(position=position(), output_format="json", json_indent=0)

    output = capsys.readouterr().out
    assert '"direction": "long"' in output
    assert '"processed_fill_ids"' in output


def test_publish_result_reports_no_fills(capsys):
    cli.publish_result(position=None, output_format="console", json_indent=2)

    assert "No fills found" in capsys.readouterr().out


def test_cli_does_not_import_analysis_runtime():
    assert "RuntimeApplicationFactory" not in cli.__dict__
    assert "SingleAnalysisCycle" not in cli.__dict__
