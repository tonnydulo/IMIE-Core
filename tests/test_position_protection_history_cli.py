from pathlib import Path

import imie.position_protection_history_cli as cli


def test_parser_defaults_to_latest_local_observation():
    arguments = cli.build_parser().parse_args(["NVDA"])

    assert arguments.position_store == Path("runtime/execution/positions.json")
    assert arguments.reconciliation_store == Path(
        "runtime/execution/position_protection_reconciliations.json"
    )
    assert arguments.all is False


def test_main_requests_latest_by_default(monkeypatch):
    calls = []

    class Service:
        def get_latest_current(self, **kwargs):
            calls.append(("latest", kwargs))
            return None

    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_history", lambda **kwargs: None)

    assert cli.main(["nvda"]) == 2
    assert calls == [("latest", {"broker": "alpaca-paper", "symbol": "nvda"})]


def test_main_requests_all_only_when_explicit(monkeypatch):
    calls = []

    class Service:
        def list_current(self, **kwargs):
            calls.append(("all", kwargs))
            return ()

    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_history", lambda **kwargs: None)

    assert cli.main(["NVDA", "--all"]) == 2
    assert calls == [("all", {"broker": "alpaca-paper", "symbol": "NVDA"})]


def test_empty_history_is_visible(capsys):
    cli.publish_history(records=(), output_format="console", json_indent=2)

    assert "No protection reconciliation observations" in capsys.readouterr().out


def test_cli_import_has_no_broker_adapter_or_runtime():
    assert "AlpacaPaperExecutionAdapter" not in cli.__dict__
    assert "RuntimeApplicationFactory" not in cli.__dict__
