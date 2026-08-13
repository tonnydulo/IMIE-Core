from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.execution import (
    JsonFilePositionProtectionReconciliationStore,
    JsonFilePositionStateStore,
    PositionProtectionReconciliationHistoryService,
)
from imie.models import PositionProtectionReconciliationRecord
from imie.position_protect_cli import BROKER_NAME, DEFAULT_POSITION_STORE
from imie.position_protection_reconcile_cli import DEFAULT_RECONCILIATION_STORE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-protection-history",
        description=(
            "Inspect locally recorded broker-truth observations for the current "
            "position fingerprint."
        ),
    )
    parser.add_argument("symbol", help="Reconciled Alpaca paper position symbol.")
    parser.add_argument("--position-store", type=Path, default=DEFAULT_POSITION_STORE)
    parser.add_argument(
        "--reconciliation-store",
        type=Path,
        default=DEFAULT_RECONCILIATION_STORE,
    )
    parser.add_argument(
        "--all", action="store_true", help="Show all current-fingerprint observations."
    )
    parser.add_argument(
        "--output-format", choices=("console", "json"), default="console"
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_service(
    *, position_store_path: Path, reconciliation_store_path: Path
) -> PositionProtectionReconciliationHistoryService:
    if not isinstance(position_store_path, Path):
        raise TypeError("position_store_path must be a Path.")
    if not isinstance(reconciliation_store_path, Path):
        raise TypeError("reconciliation_store_path must be a Path.")
    return PositionProtectionReconciliationHistoryService(
        position_store=JsonFilePositionStateStore(position_store_path),
        reconciliation_store=JsonFilePositionProtectionReconciliationStore(
            reconciliation_store_path
        ),
    )


def _record_payload(
    record: PositionProtectionReconciliationRecord,
) -> dict[str, object]:
    result = record.result
    return {
        "observed_at": record.observed_at.isoformat(),
        "position_updated_at": record.position_updated_at.isoformat(),
        "position_fill_ids": list(record.position_fill_ids),
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
                "filled_quantity": item.filled_quantity,
                "remaining_quantity": item.remaining_quantity,
                "last_updated_at": item.last_updated_at.isoformat(),
            }
            for item in result.snapshots
        ],
        "discrepancies": list(result.discrepancies),
        "warnings": list(result.warnings),
    }


def publish_history(
    *,
    records: tuple[PositionProtectionReconciliationRecord, ...],
    output_format: str,
    json_indent: int,
) -> None:
    payload = [_record_payload(item) for item in records]
    if output_format == "json":
        print(json.dumps(payload, indent=json_indent))
        return
    if output_format != "console":
        raise ValueError("output_format must be console or json.")
    if not payload:
        print("No protection reconciliation observations exist for this position.")
        return
    print("Position Protection Reconciliation History :")
    for item in payload:
        print(
            f"{item['observed_at']} | {item['state']} | "
            f"active={item['active_quantity']} | "
            f"triggered={item['triggered_quantity']} | "
            f"reconciled={item['reconciled']}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    logger = logging.getLogger("imie.position_protection_history")
    try:
        service = build_service(
            position_store_path=arguments.position_store,
            reconciliation_store_path=arguments.reconciliation_store,
        )
        if arguments.all:
            records = service.list_current(
                broker=BROKER_NAME, symbol=arguments.symbol
            )
        else:
            latest = service.get_latest_current(
                broker=BROKER_NAME, symbol=arguments.symbol
            )
            records = (latest,) if latest is not None else ()
        publish_history(
            records=records,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0 if records else 2
    except (TypeError, ValueError, LookupError, OSError) as exc:
        logger.error("Position protection history failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
