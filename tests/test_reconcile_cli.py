from argparse import Namespace
from pathlib import Path

import pytest

from imie.config.settings import AppSettings
from imie.models import BrokerOrderStatus, ExecutionReconciliationResult
import imie.reconcile_cli as cli


def result(reconciled: bool = True) -> ExecutionReconciliationResult:
    return ExecutionReconciliationResult(
        broker="alpaca-paper",
        broker_order_id="order-123",
        symbol="NVDA",
        side="buy",
        status=BrokerOrderStatus.ACCEPTED,
        intent_quantity=100,
        broker_requested_quantity=100,
        broker_filled_quantity=0,
        recorded_fill_quantity=0,
        broker_average_fill_price=None,
        recorded_average_fill_price=None,
        identity_matched=True,
        quantity_matched=True,
        fills_matched=reconciled,
        reconciled=reconciled,
        discrepancies=() if reconciled else ("fills differ",),
    )


def test_parser_defaults() -> None:
    arguments = cli.build_parser().parse_args(["order-123"])

    assert arguments.broker_order_id == "order-123"
    assert arguments.intent_store == Path(
        "runtime/execution/broker_order_intents.json"
    )
    assert arguments.output_format == "console"
    assert arguments.json_indent == 2


def test_build_service_requires_explicit_paper_mode() -> None:
    with pytest.raises(ValueError, match="ALPACA_PAPER=true"):
        cli.build_service(
            settings=AppSettings(
                alpaca_api_key="paper-key",
                alpaca_secret_key="paper-secret",
                alpaca_paper=False,
            ),
            intent_store_path=Path("intents.json"),
        )


def test_build_service_wires_read_only_query_components() -> None:
    service = cli.build_service(
        settings=AppSettings(
            alpaca_api_key="paper-key",
            alpaca_secret_key="paper-secret",
            alpaca_paper=True,
        ),
        intent_store_path=Path("custom-intents.json"),
    )

    assert service._query_port.broker_name == "alpaca-paper"
    assert service._query_port._intent_store is None
    assert service._intent_store.path == Path("custom-intents.json")


def test_main_reconciles_once_and_publishes_console(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []
    published: list[tuple[str, int]] = []

    class Service:
        def reconcile_recorded_order(self, *, broker, broker_order_id):
            calls.append((broker, broker_order_id))
            return result()

    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(
        cli,
        "publish_result",
        lambda *, result, output_format, json_indent: published.append(
            (output_format, json_indent)
        ),
    )

    exit_code = cli.main(["order-123"])

    assert exit_code == 0
    assert calls == [("alpaca-paper", "order-123")]
    assert published == [("console", 2)]


def test_main_returns_two_for_unreconciled_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Service:
        def reconcile_recorded_order(self, **kwargs):
            return result(False)

    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_result", lambda **kwargs: None)

    assert cli.main(["order-123", "--output-format", "json"]) == 2


def test_main_returns_one_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(
        cli,
        "build_service",
        lambda **kwargs: (_ for _ in ()).throw(LookupError("missing")),
    )

    assert cli.main(["order-123"]) == 1


def test_publish_result_selects_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli.publish_result(
        result=result(),
        output_format="json",
        json_indent=0,
    )

    assert '"reconciled": true' in capsys.readouterr().out


def test_cli_module_does_not_import_analysis_runtime() -> None:
    assert "RuntimeApplicationFactory" not in cli.__dict__
    assert "SingleAnalysisCycle" not in cli.__dict__
