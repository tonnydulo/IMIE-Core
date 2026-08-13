from __future__ import annotations

import argparse
import logging

from pathlib import Path
from typing import Sequence

from imie.config.settings import AppSettings, load_settings
from imie.execution import (
    AlpacaPaperExecutionAdapter,
    AlpacaPaperFillActivitySource,
    ConsoleReconciliationResultPublisher,
    ExecutionReconciliationService,
    JsonFileBrokerOrderIntentStore,
    JsonReconciliationResultPublisher,
)
from imie.models import ExecutionReconciliationResult
from imie.utils.logging_utils import configure_logging


BROKER_NAME = "alpaca-paper"
DEFAULT_INTENT_STORE = Path(
    "runtime/execution/broker_order_intents.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-reconcile",
        description=(
            "Perform one read-only reconciliation of a recorded "
            "Alpaca paper order."
        ),
    )
    parser.add_argument(
        "broker_order_id",
        help="Alpaca paper broker order ID to reconcile.",
    )
    parser.add_argument(
        "--intent-store",
        type=Path,
        default=DEFAULT_INTENT_STORE,
        help=(
            "Recorded intent JSON file. Default: "
            "runtime/execution/broker_order_intents.json."
        ),
    )
    parser.add_argument(
        "--output-format",
        choices=("console", "json"),
        default="console",
        help="Result output format. Default: console.",
    )
    parser.add_argument(
        "--json-indent",
        type=int,
        default=2,
        help="JSON indentation. Default: 2.",
    )
    return parser


def build_service(
    *,
    settings: AppSettings,
    intent_store_path: Path,
) -> ExecutionReconciliationService:
    if not isinstance(settings, AppSettings):
        raise TypeError("settings must be an AppSettings.")
    if settings.alpaca_paper is not True:
        raise ValueError("reconciliation requires ALPACA_PAPER=true.")
    if not settings.alpaca_api_key.strip() or not settings.alpaca_secret_key.strip():
        raise ValueError(
            "reconciliation requires ALPACA_API_KEY and ALPACA_SECRET_KEY."
        )
    if not isinstance(intent_store_path, Path):
        raise TypeError("intent_store_path must be a Path.")

    fill_source = AlpacaPaperFillActivitySource(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )
    adapter = AlpacaPaperExecutionAdapter(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        fill_activity_source=fill_source,
    )
    return ExecutionReconciliationService(
        query_port=adapter,
        intent_store=JsonFileBrokerOrderIntentStore(intent_store_path),
    )


def publish_result(
    *,
    result: ExecutionReconciliationResult,
    output_format: str,
    json_indent: int,
) -> None:
    if output_format == "console":
        ConsoleReconciliationResultPublisher().publish(result)
        return
    if output_format == "json":
        JsonReconciliationResultPublisher(indent=json_indent).publish(result)
        return
    raise ValueError("output_format must be console or json.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger("imie.reconcile")

    try:
        service = build_service(
            settings=settings,
            intent_store_path=arguments.intent_store,
        )
        result = service.reconcile_recorded_order(
            broker=BROKER_NAME,
            broker_order_id=arguments.broker_order_id,
        )
        publish_result(
            result=result,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0 if result.reconciled else 2
    except (TypeError, ValueError, LookupError, OSError, RuntimeError) as exc:
        logger.error("Reconciliation failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

