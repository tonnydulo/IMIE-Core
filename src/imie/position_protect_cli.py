from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.config.settings import AppSettings, load_settings
from imie.execution import (
    ExistingPositionProtectionPlanBuilder,
    JsonFilePositionStateStore,
    ProtectiveCoverageEngine,
)
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    ExistingPositionProtectionResult,
    PositionDirection,
)
from imie.utils.logging_utils import configure_logging


BROKER_NAME = "alpaca-paper"
DEFAULT_POSITION_STORE = Path("runtime/execution/positions.json")
DEFAULT_PROTECTION_STORE = Path("runtime/execution/position_protections.json")
DEFAULT_ATTEMPT_STORE = Path("runtime/execution/position_protection_attempts.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-protect",
        description=(
            "Explicitly submit stop/target OCO protection for one reconciled "
            "Alpaca paper position."
        ),
    )
    parser.add_argument("symbol", help="Reconciled Alpaca paper position symbol.")
    parser.add_argument("--stop-price", type=float, required=True)
    parser.add_argument("--target1-price", type=float, required=True)
    parser.add_argument("--target2-price", type=float, required=True)
    parser.add_argument("--time-in-force", choices=("day", "gtc"), default="gtc")
    parser.add_argument("--position-store", type=Path, default=DEFAULT_POSITION_STORE)
    parser.add_argument(
        "--protection-store", type=Path, default=DEFAULT_PROTECTION_STORE
    )
    parser.add_argument("--attempt-store", type=Path, default=DEFAULT_ATTEMPT_STORE)
    parser.add_argument(
        "--confirm-paper-protection",
        action="store_true",
        help="Required acknowledgement that paper broker orders will be submitted.",
    )
    parser.add_argument(
        "--output-format", choices=("console", "json"), default="console"
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_plan(
    *,
    position_store_path: Path,
    symbol: str,
    stop_price: float,
    target1_price: float,
    target2_price: float,
    time_in_force: str,
):
    position = JsonFilePositionStateStore(position_store_path).get(
        broker=BROKER_NAME,
        symbol=symbol,
    )
    if position is None:
        raise LookupError("No reconciled Alpaca paper position exists for symbol.")
    if not isinstance(position, ExecutionPosition):
        raise TypeError("position store must return ExecutionPosition or None.")
    if position.is_flat:
        raise ValueError("Cannot protect a flat position.")
    side = "buy" if position.direction is PositionDirection.LONG else "sell"
    intent = ExecutionOrderIntent(
        symbol=position.symbol,
        side=side,
        quantity=position.quantity,
        order_type="market",
        entry_price=None,
        stop_price=stop_price,
        target1_price=target1_price,
        target2_price=target2_price,
        time_in_force=time_in_force,
        valid=True,
        actionable=True,
        reasons=("Explicit existing-position paper protection request.",),
    )
    coverage = ProtectiveCoverageEngine().assess(
        intent=intent,
        position=position,
    )
    return ExistingPositionProtectionPlanBuilder().build(
        intent=intent,
        position=position,
        coverage=coverage,
    )


def build_service(
    *,
    settings: AppSettings,
    position_store_path: Path,
    protection_store_path: Path,
    attempt_store_path: Path,
):
    from imie.execution import AlpacaPaperPositionProtectionServiceFactory

    return AlpacaPaperPositionProtectionServiceFactory.create(
        settings=settings,
        position_store_path=position_store_path,
        protection_store_path=protection_store_path,
        attempt_store_path=attempt_store_path,
    )


def publish_result(
    *, result: ExistingPositionProtectionResult, output_format: str, json_indent: int
) -> None:
    payload = {
        "broker": result.broker,
        "symbol": result.symbol,
        "exit_side": result.exit_side,
        "requested_quantity": result.requested_quantity,
        "accepted_quantity": result.accepted_quantity,
        "accepted": result.accepted,
        "status": result.status,
        "message": result.message,
        "broker_order_ids": [
            order_id
            for item in result.submissions
            for order_id in (item.target_order_id, item.stop_order_id)
            if order_id is not None
        ],
        "rollback_attempted": result.rollback_attempted,
        "rollback_succeeded": result.rollback_succeeded,
        "warnings": list(result.warnings),
    }
    if output_format == "json":
        print(json.dumps(payload, indent=json_indent))
        return
    print("Position Protection Result :")
    for label, key in (
        ("Broker", "broker"),
        ("Symbol", "symbol"),
        ("Exit Side", "exit_side"),
        ("Requested", "requested_quantity"),
        ("Accepted Qty", "accepted_quantity"),
        ("Accepted", "accepted"),
        ("Status", "status"),
        ("Message", "message"),
    ):
        print(f"{label:<12}: {payload[key]}")
    print(f"Broker Orders: {', '.join(payload['broker_order_ids'])}")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger("imie.position_protect")
    if not arguments.confirm_paper_protection:
        logger.error("Paper protection requires --confirm-paper-protection.")
        return 2
    try:
        plan = build_plan(
            position_store_path=arguments.position_store,
            symbol=arguments.symbol,
            stop_price=arguments.stop_price,
            target1_price=arguments.target1_price,
            target2_price=arguments.target2_price,
            time_in_force=arguments.time_in_force,
        )
        service = build_service(
            settings=settings,
            position_store_path=arguments.position_store,
            protection_store_path=arguments.protection_store,
            attempt_store_path=arguments.attempt_store,
        )
        result = service.protect(plan)
        publish_result(
            result=result,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0 if result.accepted else 2
    except (TypeError, ValueError, LookupError, OSError, RuntimeError) as exc:
        logger.error("Position protection failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
