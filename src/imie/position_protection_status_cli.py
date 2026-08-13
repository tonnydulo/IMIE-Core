from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.execution import (
    JsonFilePositionProtectionAttemptStore,
    JsonFilePositionProtectionStore,
    JsonFilePositionStateStore,
    PositionProtectionStatusService,
)
from imie.models import PositionProtectionStatus
from imie.position_protect_cli import (
    BROKER_NAME,
    DEFAULT_ATTEMPT_STORE,
    DEFAULT_POSITION_STORE,
    DEFAULT_PROTECTION_STORE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-protection-status",
        description=(
            "Inspect persisted position-protection state without broker access."
        ),
    )
    parser.add_argument("symbol", help="Alpaca paper position symbol.")
    parser.add_argument("--position-store", type=Path, default=DEFAULT_POSITION_STORE)
    parser.add_argument(
        "--protection-store", type=Path, default=DEFAULT_PROTECTION_STORE
    )
    parser.add_argument("--attempt-store", type=Path, default=DEFAULT_ATTEMPT_STORE)
    parser.add_argument(
        "--output-format", choices=("console", "json"), default="console"
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_service(
    *,
    position_store_path: Path,
    protection_store_path: Path,
    attempt_store_path: Path,
) -> PositionProtectionStatusService:
    return PositionProtectionStatusService(
        position_store=JsonFilePositionStateStore(position_store_path),
        protection_store=JsonFilePositionProtectionStore(protection_store_path),
        attempt_store=JsonFilePositionProtectionAttemptStore(attempt_store_path),
    )


def _payload(status: PositionProtectionStatus) -> dict[str, object]:
    position = status.position
    attempt = status.attempt
    record = status.record
    return {
        "broker": status.broker,
        "symbol": status.symbol,
        "state": status.state,
        "position_quantity": position.quantity if position else None,
        "position_direction": position.direction.value if position else None,
        "position_updated_at": (
            position.last_updated_at.isoformat() if position else None
        ),
        "position_fill_ids": list(position.processed_fill_ids) if position else [],
        "attempt_id": attempt.attempt_id if attempt else None,
        "attempt_status": attempt.status.value if attempt else None,
        "attempt_updated_at": attempt.updated_at.isoformat() if attempt else None,
        "attempt_message": attempt.message if attempt else None,
        "protection_recorded_at": (
            record.recorded_at.isoformat() if record else None
        ),
        "accepted_quantity": (
            record.result.accepted_quantity if record else None
        ),
        "broker_order_ids": (
            [
                order_id
                for item in record.result.submissions
                for order_id in (item.target_order_id, item.stop_order_id)
                if order_id is not None
            ]
            if record
            else []
        ),
    }


def publish_status(
    *, status: PositionProtectionStatus, output_format: str, json_indent: int
) -> None:
    payload = _payload(status)
    if output_format == "json":
        print(json.dumps(payload, indent=json_indent))
        return
    print("Position Protection Status :")
    for label, key in (
        ("Broker", "broker"),
        ("Symbol", "symbol"),
        ("State", "state"),
        ("Position Qty", "position_quantity"),
        ("Direction", "position_direction"),
        ("Attempt ID", "attempt_id"),
        ("Attempt", "attempt_status"),
        ("Message", "attempt_message"),
        ("Accepted Qty", "accepted_quantity"),
    ):
        print(f"{label:<13}: {payload[key]}")
    print(f"Broker Orders: {', '.join(payload['broker_order_ids']) or 'None'}")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    logger = logging.getLogger("imie.position_protection_status")
    try:
        service = build_service(
            position_store_path=arguments.position_store,
            protection_store_path=arguments.protection_store,
            attempt_store_path=arguments.attempt_store,
        )
        status = service.get(broker=BROKER_NAME, symbol=arguments.symbol)
        publish_status(
            status=status,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0
    except (TypeError, ValueError, LookupError, OSError) as exc:
        logger.error("Position protection status failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
