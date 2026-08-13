from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.models import BrokerOrderIntentRecord, ExecutionOrderIntent


class JsonFileBrokerOrderIntentStore:
    """Atomically persist broker-order intent records as JSON."""

    schema_version = 1

    def __init__(
        self,
        path: str | Path,
        *,
        indent: int | None = 2,
        create_parent_directories: bool = True,
    ) -> None:
        if not isinstance(path, str | Path):
            raise TypeError("path must be a string or Path.")
        resolved_path = Path(path)
        if not str(resolved_path).strip():
            raise ValueError("path cannot be empty.")
        if indent is not None and (
            isinstance(indent, bool) or not isinstance(indent, int)
        ):
            raise TypeError("indent must be an int or None.")
        if indent is not None and indent < 0:
            raise ValueError("indent cannot be negative.")
        if not isinstance(create_parent_directories, bool):
            raise TypeError("create_parent_directories must be a bool.")
        self.path = resolved_path
        self.indent = indent
        self.create_parent_directories = create_parent_directories
        self._lock = RLock()

    def save(self, record: BrokerOrderIntentRecord) -> None:
        if not isinstance(record, BrokerOrderIntentRecord):
            raise TypeError("record must be a BrokerOrderIntentRecord.")
        with self._lock:
            records = self._load_records()
            if any(item.key == record.key for item in records):
                raise ValueError(
                    "A broker-order intent record already exists for "
                    f"{record.broker}/{record.broker_order_id}."
                )
            self._write_records((*records, record))

    def get(
        self,
        *,
        broker: str,
        broker_order_id: str,
    ) -> BrokerOrderIntentRecord | None:
        normalized_broker = self._required_text(broker, "broker").lower()
        normalized_order_id = self._required_text(
            broker_order_id,
            "broker_order_id",
        )
        with self._lock:
            for record in self._load_records():
                if record.key == (normalized_broker, normalized_order_id):
                    return record
        return None

    def _load_records(self) -> tuple[BrokerOrderIntentRecord, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Intent store contains malformed JSON.") from exc
        if not isinstance(payload, dict):
            raise TypeError("Intent store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError("Intent store schema_version is unsupported.")
        raw_records = payload.get("records")
        if not isinstance(raw_records, list):
            raise TypeError("Intent store records must be a list.")

        records = tuple(self._record_from_dict(item) for item in raw_records)
        keys = tuple(record.key for record in records)
        if len(set(keys)) != len(keys):
            raise ValueError("Intent store contains duplicate broker-order keys.")
        return records

    def _write_records(
        self,
        records: tuple[BrokerOrderIntentRecord, ...],
    ) -> None:
        parent = self.path.parent
        if self.create_parent_directories:
            parent.mkdir(parents=True, exist_ok=True)
        elif not parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {parent}")

        payload = {
            "schema_version": self.schema_version,
            "records": [self._record_to_dict(record) for record in records],
        }
        serialized = json.dumps(
            payload,
            indent=self.indent,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
        temporary_path = self.path.with_name(
            f".{self.path.name}.{uuid4().hex}.tmp"
        )
        try:
            with temporary_path.open("x", encoding="utf-8", newline="\n") as file:
                file.write(serialized)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    @staticmethod
    def _record_to_dict(record: BrokerOrderIntentRecord) -> dict[str, object]:
        intent = record.intent
        return {
            "broker": record.broker,
            "broker_order_id": record.broker_order_id,
            "recorded_at": record.recorded_at.isoformat(),
            "submission_label": record.submission_label,
            "intent": {
                "symbol": intent.symbol,
                "side": intent.side,
                "quantity": intent.quantity,
                "order_type": intent.order_type,
                "entry_price": intent.entry_price,
                "stop_price": intent.stop_price,
                "target1_price": intent.target1_price,
                "target2_price": intent.target2_price,
                "time_in_force": intent.time_in_force,
                "valid": intent.valid,
                "actionable": intent.actionable,
                "reasons": list(intent.reasons),
                "warnings": list(intent.warnings),
            },
        }

    @staticmethod
    def _record_from_dict(value: object) -> BrokerOrderIntentRecord:
        if not isinstance(value, dict):
            raise TypeError("Intent store record must be an object.")
        intent_value = value.get("intent")
        if not isinstance(intent_value, dict):
            raise TypeError("Intent store record intent must be an object.")
        try:
            intent = ExecutionOrderIntent(
                symbol=intent_value["symbol"],
                side=intent_value["side"],
                quantity=intent_value["quantity"],
                order_type=intent_value["order_type"],
                entry_price=intent_value["entry_price"],
                stop_price=intent_value["stop_price"],
                target1_price=intent_value["target1_price"],
                target2_price=intent_value["target2_price"],
                time_in_force=intent_value["time_in_force"],
                valid=intent_value["valid"],
                actionable=intent_value["actionable"],
                reasons=JsonFileBrokerOrderIntentStore._string_tuple(
                    intent_value.get("reasons", []), "reasons"
                ),
                warnings=JsonFileBrokerOrderIntentStore._string_tuple(
                    intent_value.get("warnings", []), "warnings"
                ),
            )
            recorded_at_value = value["recorded_at"]
            if not isinstance(recorded_at_value, str):
                raise TypeError("recorded_at must be a string.")
            recorded_at = datetime.fromisoformat(recorded_at_value)
            return BrokerOrderIntentRecord(
                broker=value["broker"],
                broker_order_id=value["broker_order_id"],
                intent=intent,
                recorded_at=recorded_at,
                submission_label=value.get("submission_label"),
            )
        except KeyError as exc:
            raise ValueError(
                f"Intent store record is missing required field {exc.args[0]!r}."
            ) from exc

    @staticmethod
    def _string_tuple(value: object, name: str) -> tuple[str, ...]:
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise TypeError(f"Intent store {name} must be a list of strings.")
        return tuple(value)

    @staticmethod
    def _required_text(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{name} cannot be empty.")
        return normalized
