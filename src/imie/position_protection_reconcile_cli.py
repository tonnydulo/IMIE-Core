from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.config.settings import AppSettings, load_settings
from imie.models import PositionProtectionReconciliationResult
from imie.position_protect_cli import (
    BROKER_NAME,
    DEFAULT_POSITION_STORE,
    DEFAULT_PROTECTION_STORE,
)
from imie.utils.logging_utils import configure_logging


DEFAULT_RECONCILIATION_STORE = Path(
    "runtime/execution/position_protection_reconciliations.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-protection-reconcile",
        description=(
            "Perform one read-only reconciliation of recorded Alpaca paper "
            "position protection."
        ),
    )
    parser.add_argument("symbol", help="Reconciled Alpaca paper position symbol.")
    parser.add_argument("--position-store", type=Path, default=DEFAULT_POSITION_STORE)
    parser.add_argument(
        "--protection-store", type=Path, default=DEFAULT_PROTECTION_STORE
    )
    parser.add_argument(
        "--reconciliation-store",
        type=Path,
        default=DEFAULT_RECONCILIATION_STORE,
    )
    parser.add_argument(
        "--output-format", choices=("console", "json"), default="console"
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_service(
    *,
    settings: AppSettings,
    position_store_path: Path,
    protection_store_path: Path,
    reconciliation_store_path: Path,
):
    if not isinstance(settings, AppSettings):
        raise TypeError("settings must be an AppSettings.")
    if settings.alpaca_paper is not True:
        raise ValueError("protection reconciliation requires ALPACA_PAPER=true.")
    if not settings.alpaca_api_key.strip() or not settings.alpaca_secret_key.strip():
        raise ValueError(
            "protection reconciliation requires ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY."
        )
    if not isinstance(position_store_path, Path):
        raise TypeError("position_store_path must be a Path.")
    if not isinstance(protection_store_path, Path):
        raise TypeError("protection_store_path must be a Path.")
    if not isinstance(reconciliation_store_path, Path):
        raise TypeError("reconciliation_store_path must be a Path.")

    from imie.execution import (
        AlpacaPaperExecutionAdapter,
        JsonFilePositionProtectionStore,
        JsonFilePositionProtectionReconciliationStore,
        JsonFilePositionStateStore,
        PositionProtectionReconciliationService,
    )

    adapter = AlpacaPaperExecutionAdapter(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )
    return PositionProtectionReconciliationService(
        position_store=JsonFilePositionStateStore(position_store_path),
        protection_store=JsonFilePositionProtectionStore(protection_store_path),
        query_port=adapter,
        reconciliation_store=JsonFilePositionProtectionReconciliationStore(
            reconciliation_store_path
        ),
    )


def _payload(result: PositionProtectionReconciliationResult) -> dict[str, object]:
    return {
        "broker": result.broker,
        "symbol": result.symbol,
        "state": result.state,
        "requested_quantity": result.requested_quantity,
        "active_quantity": result.active_quantity,
        "triggered_quantity": result.triggered_quantity,
        "reconciled": result.reconciled,
        "broker_orders": [
            {
                "broker_order_id": item.broker_order_id,
                "status": item.status.value,
                "side": item.side,
                "requested_quantity": item.requested_quantity,
                "filled_quantity": item.filled_quantity,
                "remaining_quantity": item.remaining_quantity,
                "average_fill_price": item.average_fill_price,
                "rejection_reason": item.rejection_reason,
                "last_updated_at": item.last_updated_at.isoformat(),
            }
            for item in result.snapshots
        ],
        "discrepancies": list(result.discrepancies),
        "warnings": list(result.warnings),
    }


def publish_result(
    *,
    result: PositionProtectionReconciliationResult,
    output_format: str,
    json_indent: int,
) -> None:
    payload = _payload(result)
    if output_format == "json":
        print(json.dumps(payload, indent=json_indent))
        return
    if output_format != "console":
        raise ValueError("output_format must be console or json.")
    print("Position Protection Reconciliation :")
    for label, key in (
        ("Broker", "broker"),
        ("Symbol", "symbol"),
        ("State", "state"),
        ("Requested", "requested_quantity"),
        ("Active", "active_quantity"),
        ("Triggered", "triggered_quantity"),
        ("Reconciled", "reconciled"),
    ):
        print(f"{label:<11}: {payload[key]}")
    print("Broker Orders:")
    for order in payload["broker_orders"]:
        print(
            f"  {order['broker_order_id']} | {order['status']} | "
            f"filled={order['filled_quantity']} | "
            f"remaining={order['remaining_quantity']}"
        )
    for discrepancy in payload["discrepancies"]:
        print(f"Discrepancy: {discrepancy}")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger("imie.position_protection_reconcile")
    try:
        service = build_service(
            settings=settings,
            position_store_path=arguments.position_store,
            protection_store_path=arguments.protection_store,
            reconciliation_store_path=arguments.reconciliation_store,
        )
        result = service.reconcile(broker=BROKER_NAME, symbol=arguments.symbol)
        publish_result(
            result=result,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0 if result.state in {"active", "triggered"} else 2
    except (TypeError, ValueError, LookupError, OSError, RuntimeError) as exc:
        logger.error("Position protection reconciliation failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
