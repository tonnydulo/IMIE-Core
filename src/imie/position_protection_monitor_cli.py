from __future__ import annotations

import argparse
import json
import logging

from pathlib import Path
from typing import Sequence

from imie.execution import (
    JsonFilePositionProtectionReconciliationStore,
    JsonFilePositionStateStore,
    PositionProtectionMonitoringEngine,
    PositionProtectionMonitoringService,
    PositionProtectionReconciliationHistoryService,
)
from imie.models import PositionProtectionMonitoringAssessment
from imie.position_protect_cli import BROKER_NAME, DEFAULT_POSITION_STORE
from imie.position_protection_reconcile_cli import DEFAULT_RECONCILIATION_STORE


DEFAULT_MAXIMUM_AGE_SECONDS = 30.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-position-protection-monitor",
        description=(
            "Assess the latest local protection observation for the current "
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
        "--maximum-age-seconds",
        type=float,
        default=DEFAULT_MAXIMUM_AGE_SECONDS,
        help="Maximum healthy observation age. Default: 30 seconds.",
    )
    parser.add_argument(
        "--output-format", choices=("console", "json"), default="console"
    )
    parser.add_argument("--json-indent", type=int, default=2)
    return parser


def build_service(
    *,
    position_store_path: Path,
    reconciliation_store_path: Path,
    maximum_age_seconds: float,
) -> PositionProtectionMonitoringService:
    if not isinstance(position_store_path, Path):
        raise TypeError("position_store_path must be a Path.")
    if not isinstance(reconciliation_store_path, Path):
        raise TypeError("reconciliation_store_path must be a Path.")
    history = PositionProtectionReconciliationHistoryService(
        position_store=JsonFilePositionStateStore(position_store_path),
        reconciliation_store=JsonFilePositionProtectionReconciliationStore(
            reconciliation_store_path
        ),
    )
    return PositionProtectionMonitoringService(
        history_service=history,
        engine=PositionProtectionMonitoringEngine(
            maximum_age_seconds=maximum_age_seconds
        ),
    )


def _payload(
    assessment: PositionProtectionMonitoringAssessment,
) -> dict[str, object]:
    return {
        "broker": assessment.broker,
        "symbol": assessment.symbol,
        "state": assessment.state,
        "checked_at": assessment.checked_at.isoformat(),
        "observed_at": (
            assessment.observed_at.isoformat()
            if assessment.observed_at is not None
            else None
        ),
        "observation_age_seconds": assessment.observation_age_seconds,
        "maximum_age_seconds": assessment.maximum_age_seconds,
        "reconciliation_state": assessment.reconciliation_state,
        "healthy": assessment.healthy,
        "action_required": assessment.action_required,
        "reason": assessment.reason,
        "warnings": list(assessment.warnings),
    }


def publish_assessment(
    *,
    assessment: PositionProtectionMonitoringAssessment,
    output_format: str,
    json_indent: int,
) -> None:
    payload = _payload(assessment)
    if output_format == "json":
        print(json.dumps(payload, indent=json_indent))
        return
    if output_format != "console":
        raise ValueError("output_format must be console or json.")
    print("Position Protection Monitor :")
    for label, key in (
        ("Broker", "broker"),
        ("Symbol", "symbol"),
        ("State", "state"),
        ("Observed", "observed_at"),
        ("Age Seconds", "observation_age_seconds"),
        ("Maximum Age", "maximum_age_seconds"),
        ("Broker Truth", "reconciliation_state"),
        ("Healthy", "healthy"),
        ("Action Needed", "action_required"),
        ("Reason", "reason"),
    ):
        print(f"{label:<14}: {payload[key]}")
    for warning in payload["warnings"]:
        print(f"Warning       : {warning}")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    logger = logging.getLogger("imie.position_protection_monitor")
    try:
        service = build_service(
            position_store_path=arguments.position_store,
            reconciliation_store_path=arguments.reconciliation_store,
            maximum_age_seconds=arguments.maximum_age_seconds,
        )
        assessment = service.assess(
            broker=BROKER_NAME,
            symbol=arguments.symbol,
        )
        publish_assessment(
            assessment=assessment,
            output_format=arguments.output_format,
            json_indent=arguments.json_indent,
        )
        return 0 if assessment.healthy else 2
    except (TypeError, ValueError, LookupError, OSError) as exc:
        logger.error("Position protection monitoring failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
