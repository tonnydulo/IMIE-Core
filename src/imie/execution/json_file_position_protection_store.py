from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.models import (
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionProtectionRecord,
)


class JsonFilePositionProtectionStore:
    """Atomically persist accepted protection keyed to position fingerprint."""

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

    def save(self, record: PositionProtectionRecord) -> None:
        if not isinstance(record, PositionProtectionRecord):
            raise TypeError("record must be a PositionProtectionRecord.")
        with self._lock:
            records = self._load()
            if any(item.key == record.key for item in records):
                raise ValueError(
                    "Accepted protection already exists for this position fingerprint."
                )
            self._write((*records, record))

    def get_for_position(
        self,
        *,
        broker: str,
        symbol: str,
        position_updated_at: datetime,
        position_fill_ids: tuple[str, ...],
    ) -> PositionProtectionRecord | None:
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
        key = (
            broker.strip().lower(),
            symbol.strip().upper(),
            position_updated_at,
            tuple(item.strip() for item in position_fill_ids if item.strip()),
        )
        with self._lock:
            return next((item for item in self._load() if item.key == key), None)

    def _load(self) -> tuple[PositionProtectionRecord, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Protection store contains malformed JSON.") from exc
        if not isinstance(payload, dict):
            raise TypeError("Protection store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError("Protection store schema_version is unsupported.")
        values = payload.get("records")
        if not isinstance(values, list):
            raise TypeError("Protection store records must be a list.")
        records = tuple(self._from_dict(value) for value in values)
        keys = tuple(item.key for item in records)
        if len(set(keys)) != len(keys):
            raise ValueError("Protection store contains duplicate position keys.")
        return records

    def _write(self, records: tuple[PositionProtectionRecord, ...]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.schema_version,
            "records": [self._to_dict(item) for item in records],
        }
        serialized = json.dumps(
            payload, indent=self.indent, sort_keys=True, allow_nan=False
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
    def _to_dict(record: PositionProtectionRecord) -> dict[str, object]:
        result = record.result
        return {
            "recorded_at": record.recorded_at.isoformat(),
            "position_fill_ids": list(record.position_fill_ids),
            "result": {
                "broker": result.broker,
                "symbol": result.symbol,
                "exit_side": result.exit_side,
                "position_quantity": result.position_quantity,
                "requested_quantity": result.requested_quantity,
                "accepted_quantity": result.accepted_quantity,
                "position_updated_at": result.position_updated_at.isoformat(),
                "accepted": result.accepted,
                "status": result.status,
                "message": result.message,
                "rollback_attempted": result.rollback_attempted,
                "rollback_succeeded": result.rollback_succeeded,
                "warnings": list(result.warnings),
                "submissions": [
                    {
                        "label": item.label,
                        "quantity": item.quantity,
                        "accepted": item.accepted,
                        "target_order_id": item.target_order_id,
                        "stop_order_id": item.stop_order_id,
                        "status": item.status,
                        "message": item.message,
                    }
                    for item in result.submissions
                ],
            },
        }

    @staticmethod
    def _from_dict(value: object) -> PositionProtectionRecord:
        if not isinstance(value, dict) or not isinstance(value.get("result"), dict):
            raise TypeError("Protection store record must contain a result object.")
        result = value["result"]
        try:
            submissions = tuple(
                ExistingPositionProtectionSubmission(**item)
                for item in result["submissions"]
            )
            protection_result = ExistingPositionProtectionResult(
                broker=result["broker"], symbol=result["symbol"],
                exit_side=result["exit_side"],
                position_quantity=result["position_quantity"],
                requested_quantity=result["requested_quantity"],
                accepted_quantity=result["accepted_quantity"],
                position_updated_at=datetime.fromisoformat(result["position_updated_at"]),
                accepted=result["accepted"], status=result["status"],
                message=result["message"], submissions=submissions,
                rollback_attempted=result.get("rollback_attempted", False),
                rollback_succeeded=result.get("rollback_succeeded"),
                warnings=tuple(result.get("warnings", [])),
            )
            return PositionProtectionRecord(
                result=protection_result,
                position_fill_ids=tuple(value["position_fill_ids"]),
                recorded_at=datetime.fromisoformat(value["recorded_at"]),
            )
        except KeyError as exc:
            raise ValueError(
                f"Protection store record is missing field {exc.args[0]!r}."
            ) from exc
