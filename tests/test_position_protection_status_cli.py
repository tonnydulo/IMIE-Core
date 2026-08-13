from pathlib import Path

import imie.position_protection_status_cli as cli
from imie.models import PositionProtectionStatus


def test_parser_defaults():
    arguments = cli.build_parser().parse_args(["NVDA"])

    assert arguments.position_store == Path("runtime/execution/positions.json")
    assert arguments.output_format == "console"


def test_main_performs_read_only_status_query(monkeypatch):
    calls = []
    status = PositionProtectionStatus(
        broker="alpaca-paper",
        symbol="NVDA",
        state="no_position",
        position=None,
        attempt=None,
        record=None,
    )

    class Service:
        def get(self, **kwargs):
            calls.append(kwargs)
            return status

    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_status", lambda **kwargs: None)

    assert cli.main(["nvda"]) == 0
    assert calls == [{"broker": "alpaca-paper", "symbol": "nvda"}]


def test_publish_status_renders_json(capsys):
    status = PositionProtectionStatus(
        broker="alpaca-paper",
        symbol="NVDA",
        state="no_position",
        position=None,
        attempt=None,
        record=None,
    )

    cli.publish_status(status=status, output_format="json", json_indent=0)

    assert '"state": "no_position"' in capsys.readouterr().out


def test_cli_has_no_broker_adapter_or_analysis_runtime():
    assert "TradingClient" not in cli.__dict__
    assert "RuntimeApplicationFactory" not in cli.__dict__
