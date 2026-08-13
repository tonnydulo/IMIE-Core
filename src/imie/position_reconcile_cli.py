from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.config.settings import AppSettings, load_settings
from imie.execution import (
    AlpacaPaperExecutionAdapter,
    AlpacaPaperFillActivitySource,
    JsonFilePositionStateStore,
    PositionReconciliationService,
)
from imie.models import ExecutionPosition
from imie.utils.logging_utils import configure_logging


BROKER_NAME = "alpaca-paper"
DEFAULT_POSITION_STORE = Path("runtime/execution/positions.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-reconcile",
        description=(
            "Apply recorded Alpaca paper fills to broker-neutral position state."
        ),
    )
    parser.add_argument("broker_order_id", help="Alpaca paper broker order ID.")
    parser.add_argument("symbol", help="Expected symbol for the order fills.")
    parser.add_argument(
        "--position-store",
        type=Path,
        default=DEFAULT_POSITION_STORE,
        help="Position JSON file. Default: runtime/execution/positions.json.",
    )
    parser.add_argument(
        "--market-price",
        type=float,
        default=None,
        help="Optional current market price used to calculate unrealized P&L.",
    )
    parser.add_argument(
        "--output-format",
        choices=("console", "json"),
        default="console",
        help="Result output format. Default: console.",
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_service(
    *, settings: AppSettings, position_store_path: Path
) -> PositionReconciliationService:
    if not isinstance(settings, AppSettings):
        raise TypeError("settings must be an AppSettings.")
    if settings.alpaca_paper is not True:
        raise ValueError("position reconciliation requires ALPACA_PAPER=true.")
    if not settings.alpaca_api_key.strip() or not settings.alpaca_secret_key.strip():
        raise ValueError(
            "position reconciliation requires ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY."
        )
    if not isinstance(position_store_path, Path):
        raise TypeError("position_store_path must be a Path.")

    fill_source = AlpacaPaperFillActivitySource(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )
    adapter = AlpacaPaperExecutionAdapter(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        fill_activity_source=fill_source,
    )
    return PositionReconciliationService(
        query_port=adapter,
        position_store=JsonFilePositionStateStore(position_store_path),
    )


def publish_result(
    *, position: ExecutionPosition | None, output_format: str, json_indent: int
) -> None:
    if output_format not in {"console", "json"}:
        raise ValueError("output_format must be console or json.")
    if position is None:
        print("No fills found; position state was not changed.")
        return
    if output_format == "json":
        print(json.dumps(_position_dict(position), indent=json_indent))
        return
    print("Position Reconciliation :")
    print(f"Broker       : {position.broker}")
    print(f"Symbol       : {position.symbol}")
    print(f"Direction    : {position.direction.value}")
    print(f"Quantity     : {position.quantity}")
    print(f"Average Entry: {position.average_entry_price}")
    print(f"Market Price : {position.market_price}")
    print(f"Unrealized P&L: {position.unrealized_pnl}")
    print(f"Realized P&L : {position.realized_pnl}")
    print(f"Processed Fills: {len(position.processed_fill_ids)}")


def _position_dict(position: ExecutionPosition) -> dict[str, object]:
    return {
        "broker": position.broker,
        "symbol": position.symbol,
        "direction": position.direction.value,
        "quantity": position.quantity,
        "average_entry_price": position.average_entry_price,
        "market_price": position.market_price,
        "unrealized_pnl": position.unrealized_pnl,
        "realized_pnl": position.realized_pnl,
        "last_updated_at": position.last_updated_at.isoformat(),
        "warnings": list(position.warnings),
        "processed_fill_ids": list(position.processed_fill_ids),
    }


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger("imie.position_reconcile")
    try:
        service = build_service(
            settings=settings,
            position_store_path=arguments.position_store,
        )
        position = service.reconcile_order_position(
            broker=BROKER_NAME,
            broker_order_id=arguments.broker_order_id,
            symbol=arguments.symbol,
            market_price=arguments.market_price,
        )
        publish_result(
            position=position,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0
    except (TypeError, ValueError, LookupError, OSError, RuntimeError) as exc:
        logger.error("Position reconciliation failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
