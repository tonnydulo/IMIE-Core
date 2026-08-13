from datetime import datetime, timezone
from pathlib import Path

import pytest

import imie.position_protect_cli as cli
from imie.config.settings import AppSettings
from imie.execution import JsonFilePositionStateStore
from imie.models import (
    ExecutionPosition,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionDirection,
)


NOW = datetime(2026, 8, 13, 21, 0, tzinfo=timezone.utc)


def position(direction=PositionDirection.LONG):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=direction,
        quantity=3,
        average_entry_price=200.0,
        market_price=201.0,
        unrealized_pnl=3.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def save_position(tmp_path, value=None):
    path = tmp_path / "positions.json"
    JsonFilePositionStateStore(path).save(value or position())
    return path


def args(*extra):
    return [
        "NVDA",
        "--stop-price", "199",
        "--target1-price", "201",
        "--target2-price", "202",
        *extra,
    ]


def result(accepted=True):
    submissions = (
        ExistingPositionProtectionSubmission(
            label="target1",
            quantity=2,
            accepted=accepted,
            target_order_id="target-1" if accepted else None,
            stop_order_id="stop-1" if accepted else None,
            status="accepted" if accepted else "rejected",
            message="paper result",
        ),
        ExistingPositionProtectionSubmission(
            label="target2",
            quantity=1,
            accepted=accepted,
            target_order_id="target-2" if accepted else None,
            stop_order_id="stop-2" if accepted else None,
            status="accepted" if accepted else "rejected",
            message="paper result",
        ),
    )
    return ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=3,
        requested_quantity=3,
        accepted_quantity=3 if accepted else 0,
        position_updated_at=NOW,
        accepted=accepted,
        status="accepted" if accepted else "rejected",
        message="paper result",
        submissions=submissions,
    )


def test_parser_defaults_and_confirmation_is_off():
    parsed = cli.build_parser().parse_args(args())

    assert parsed.position_store == Path("runtime/execution/positions.json")
    assert parsed.protection_store == Path(
        "runtime/execution/position_protections.json"
    )
    assert parsed.attempt_store == Path(
        "runtime/execution/position_protection_attempts.json"
    )
    assert parsed.confirm_paper_protection is False


def test_build_plan_uses_reconciled_position_fingerprint(tmp_path):
    plan = cli.build_plan(
        position_store_path=save_position(tmp_path),
        symbol="nvda",
        stop_price=199.0,
        target1_price=201.0,
        target2_price=202.0,
        time_in_force="gtc",
    )

    assert plan.position_quantity == 3
    assert plan.position_updated_at == NOW
    assert plan.position_fill_ids == ("fill-1",)
    assert [item.quantity for item in plan.slices] == [2, 1]


def test_build_plan_rejects_wrong_price_geometry(tmp_path):
    with pytest.raises(ValueError, match="do not protect"):
        cli.build_plan(
            position_store_path=save_position(tmp_path),
            symbol="NVDA",
            stop_price=201.0,
            target1_price=202.0,
            target2_price=203.0,
            time_in_force="gtc",
        )


def test_main_does_not_build_or_submit_without_confirmation(monkeypatch):
    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(
        cli,
        "build_plan",
        lambda **kwargs: pytest.fail("plan must not be built"),
    )

    assert cli.main(args()) == 2


def test_main_explicitly_protects_once(monkeypatch):
    calls = []

    class Service:
        def protect(self, plan):
            calls.append(plan)
            return result()

    plan = object()
    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_plan", lambda **kwargs: plan)
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_result", lambda **kwargs: None)

    assert cli.main(args("--confirm-paper-protection")) == 0
    assert calls == [plan]


def test_main_returns_two_when_broker_rejects(monkeypatch):
    class Service:
        def protect(self, plan):
            return result(accepted=False)

    monkeypatch.setattr(cli, "load_settings", lambda: AppSettings())
    monkeypatch.setattr(cli, "build_plan", lambda **kwargs: object())
    monkeypatch.setattr(cli, "build_service", lambda **kwargs: Service())
    monkeypatch.setattr(cli, "publish_result", lambda **kwargs: None)

    assert cli.main(args("--confirm-paper-protection")) == 2


def test_publish_result_renders_json(capsys):
    cli.publish_result(result=result(), output_format="json", json_indent=0)

    output = capsys.readouterr().out
    assert '"accepted": true' in output
    assert '"target-1"' in output


def test_cli_does_not_import_analysis_runtime():
    assert "RuntimeApplicationFactory" not in cli.__dict__
    assert "SingleAnalysisCycle" not in cli.__dict__
