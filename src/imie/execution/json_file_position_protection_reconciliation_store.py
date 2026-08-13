from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    PositionProtectionReconciliationRecord,
    PositionProtectionReconciliationResult,
)


class JsonFilePositionProtectionReconciliationStore:
    """Atomically append broker-truth observations for position protection."""

    schema_version = 1

    def __init__(self, path: str | Path, *, indent: int | None = 2) -> None:
        if not isinstance(path, str | Path):
            raise TypeError("path must be a string or Path.")
        self.path = Path(path)
        if not str(self.path).strip():
            raise ValueError("path cannot be empty.")
        if indent is not None and (
            isinstance(indent, bool) or not isinstance(indent, int)
        ):
            raise TypeError("indent must be an int or None.")
        if indent is not None and indent < 0:
            raise ValueError("indent cannot be negative.")
        self.indent = indent
        self._lock = RLock()

    def save(self, record: PositionProtectionReconciliationRecord) -> None:
        if not isinstance(record, PositionProtectionReconciliationRecord):
            raise TypeError(
                "record must be a PositionProtectionReconciliationRecord."
            )
        with self._lock:
            records = self._load()
            if any(item.key == record.key for item in records):
                raise ValueError(
                    "A reconciliation observation already exists for this key."
                )
            self._write((*records, record))

    def list_for_position(self, **key) -> tuple[PositionProtectionReconciliationRecord, ...]:
        position_key = self._position_key(**key)
        with self._lock:
            return tuple(
                item for item in self._load() if item.position_key == position_key
            )

    def get_latest_for_position(self, **key) -> PositionProtectionReconciliationRecord | None:
        records = self.list_for_position(**key)
        return max(records, key=lambda item: item.observed_at, default=None)

    def _load(self) -> tuple[PositionProtectionReconciliationRecord, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Protection reconciliation store contains malformed JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise TypeError("Protection reconciliation store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError(
                "Protection reconciliation store schema_version is unsupported."
            )
        values = payload.get("records")
        if not isinstance(values, list):
            raise TypeError("Protection reconciliation records must be a list.")
        records = tuple(self._from_dict(item) for item in values)
        if len({item.key for item in records}) != len(records):
            raise ValueError("Protection reconciliation store contains duplicate keys.")
        return records

    def _write(self, records: tuple[PositionProtectionReconciliationRecord, ...]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(
            {
                "schema_version": self.schema_version,
                "records": [self._to_dict(item) for item in records],
            },
            indent=self.indent,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
        temporary = self.path.with_name(f".{self.path.name}.{uuid4().hex}.tmp")
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as file:
                file.write(serialized)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()

    @staticmethod
    def _to_dict(record: PositionProtectionReconciliationRecord) -> dict[str, object]:
        return {
            "position_updated_at": record.position_updated_at.isoformat(),
            "position_fill_ids": list(record.position_fill_ids),
            "observed_at": record.observed_at.isoformat(),
            "result": {
                "broker": record.result.broker,
                "symbol": record.result.symbol,
                "state": record.result.state,
                "requested_quantity": record.result.requested_quantity,
                "active_quantity": record.result.active_quantity,
                "triggered_quantity": record.result.triggered_quantity,
                "reconciled": record.result.reconciled,
                "discrepancies": list(record.result.discrepancies),
                "warnings": list(record.result.warnings),
                "snapshots": [
                    {
                        name: (
                            value.value
                            if isinstance(value, BrokerOrderStatus)
                            else value.isoformat()
                            if isinstance(value, datetime)
                            else value
                        )
                        for name, value in (
                            ("broker", item.broker),
                            ("broker_order_id", item.broker_order_id),
                            ("symbol", item.symbol),
                            ("side", item.side),
                            ("order_type", item.order_type),
                            ("status", item.status),
                            ("requested_quantity", item.requested_quantity),
                            ("filled_quantity", item.filled_quantity),
                            ("remaining_quantity", item.remaining_quantity),
                            ("last_updated_at", item.last_updated_at),
                            ("client_order_id", item.client_order_id),
                            ("average_fill_price", item.average_fill_price),
                            ("submitted_at", item.submitted_at),
                            ("accepted_at", item.accepted_at),
                            ("filled_at", item.filled_at),
                            ("canceled_at", item.canceled_at),
                            ("rejection_reason", item.rejection_reason),
                            ("warnings", list(item.warnings)),
                        )
                    }
                    for item in record.result.snapshots
                ],
            },
        }

    @staticmethod
    def _from_dict(value: object) -> PositionProtectionReconciliationRecord:
        if not isinstance(value, dict) or not isinstance(value.get("result"), dict):
            raise TypeError("Reconciliation record must contain a result object.")
        try:
            result = value["result"]
            snapshots = []
            for item in result["snapshots"]:
                converted = dict(item)
                converted["status"] = BrokerOrderStatus(converted["status"])
                for name in (
                    "last_updated_at", "submitted_at", "accepted_at",
                    "filled_at", "canceled_at",
                ):
                    if converted.get(name) is not None:
                        converted[name] = datetime.fromisoformat(converted[name])
                converted["warnings"] = tuple(converted.get("warnings", []))
                snapshots.append(BrokerOrderSnapshot(**converted))
            reconciliation = PositionProtectionReconciliationResult(
                broker=result["broker"], symbol=result["symbol"],
                state=result["state"],
                requested_quantity=result["requested_quantity"],
                active_quantity=result["active_quantity"],
                triggered_quantity=result["triggered_quantity"],
                reconciled=result["reconciled"], snapshots=tuple(snapshots),
                discrepancies=tuple(result.get("discrepancies", [])),
                warnings=tuple(result.get("warnings", [])),
            )
            return PositionProtectionReconciliationRecord(
                result=reconciliation,
                position_updated_at=datetime.fromisoformat(value["position_updated_at"]),
                position_fill_ids=tuple(value["position_fill_ids"]),
                observed_at=datetime.fromisoformat(value["observed_at"]),
            )
        except KeyError as exc:
            raise ValueError(
                f"Protection reconciliation record is missing field {exc.args[0]!r}."
            ) from exc

    @staticmethod
    def _position_key(
        *, broker: str, symbol: str, position_updated_at: datetime,
        position_fill_ids: tuple[str, ...]
    ) -> tuple[str, str, datetime, tuple[str, ...]]:
        if not isinstance(broker, str) or not broker.strip():
            raise ValueError("broker must be a non-empty string.")
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        if not isinstance(position_updated_at, datetime):
            raise TypeError("position_updated_at must be a datetime.")
        if position_updated_at.tzinfo is None:
            raise ValueError("position_updated_at must be timezone-aware.")
        if not isinstance(position_fill_ids, tuple) or not all(
            isinstance(item, str) for item in position_fill_ids
        ):
            raise TypeError("position_fill_ids must be a tuple of strings.")
        return (
            broker.strip().lower(), symbol.strip().upper(), position_updated_at,
            tuple(item.strip() for item in position_fill_ids if item.strip()),
        )
