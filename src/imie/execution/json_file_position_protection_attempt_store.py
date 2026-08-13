from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.execution.json_file_position_protection_store import (
    JsonFilePositionProtectionStore,
)
from imie.models import (
    PositionProtectionAttempt,
    PositionProtectionAttemptStatus,
    PositionProtectionRecord,
)


class JsonFilePositionProtectionAttemptStore:
    """Atomically reserve and transition position-protection attempts."""

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

    def reserve(self, attempt: PositionProtectionAttempt) -> None:
        if not isinstance(attempt, PositionProtectionAttempt):
            raise TypeError("attempt must be a PositionProtectionAttempt.")
        if attempt.status is not PositionProtectionAttemptStatus.RESERVED:
            raise ValueError("a new attempt must have reserved status.")
        with self._lock:
            attempts = self._load()
            if any(item.key == attempt.key for item in attempts):
                raise ValueError(
                    "A protection attempt already exists for this position fingerprint."
                )
            if any(item.attempt_id == attempt.attempt_id for item in attempts):
                raise ValueError("position protection attempt_id already exists.")
            self._write((*attempts, attempt))

    def transition(self, attempt: PositionProtectionAttempt) -> None:
        if not isinstance(attempt, PositionProtectionAttempt):
            raise TypeError("attempt must be a PositionProtectionAttempt.")
        if attempt.status is PositionProtectionAttemptStatus.RESERVED:
            raise ValueError("transition status must be terminal.")
        with self._lock:
            attempts = list(self._load())
            for index, current in enumerate(attempts):
                if current.attempt_id != attempt.attempt_id:
                    continue
                if current.status is not PositionProtectionAttemptStatus.RESERVED:
                    raise ValueError("a terminal protection attempt cannot transition.")
                if current.key != attempt.key or current.created_at != attempt.created_at:
                    raise ValueError("attempt transition fingerprint does not match reservation.")
                attempts[index] = attempt
                self._write(tuple(attempts))
                return
            raise LookupError("No reserved protection attempt exists for attempt_id.")

    def get_for_position(
        self, *, broker: str, symbol: str, position_updated_at: datetime,
        position_fill_ids: tuple[str, ...]
    ) -> PositionProtectionAttempt | None:
        key = self._key(
            broker, symbol, position_updated_at, position_fill_ids
        )
        with self._lock:
            return next((item for item in self._load() if item.key == key), None)

    def _load(self) -> tuple[PositionProtectionAttempt, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Protection attempt store contains malformed JSON.") from exc
        if not isinstance(payload, dict):
            raise TypeError("Protection attempt store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError("Protection attempt store schema_version is unsupported.")
        values = payload.get("attempts")
        if not isinstance(values, list):
            raise TypeError("Protection attempt store attempts must be a list.")
        attempts = tuple(self._from_dict(item) for item in values)
        if len({item.key for item in attempts}) != len(attempts):
            raise ValueError("Protection attempt store contains duplicate position keys.")
        if len({item.attempt_id for item in attempts}) != len(attempts):
            raise ValueError("Protection attempt store contains duplicate attempt IDs.")
        return attempts

    def _write(self, attempts: tuple[PositionProtectionAttempt, ...]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(
            {"schema_version": self.schema_version,
             "attempts": [self._to_dict(item) for item in attempts]},
            indent=self.indent, sort_keys=True, allow_nan=False,
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
    def _to_dict(attempt: PositionProtectionAttempt) -> dict[str, object]:
        result = None
        if attempt.result is not None:
            result = JsonFilePositionProtectionStore._to_dict(
                PositionProtectionRecord(
                    result=attempt.result,
                    position_fill_ids=attempt.position_fill_ids,
                    recorded_at=attempt.updated_at,
                )
            )["result"]
        return {
            "attempt_id": attempt.attempt_id, "broker": attempt.broker,
            "symbol": attempt.symbol,
            "position_updated_at": attempt.position_updated_at.isoformat(),
            "position_fill_ids": list(attempt.position_fill_ids),
            "status": attempt.status.value,
            "created_at": attempt.created_at.isoformat(),
            "updated_at": attempt.updated_at.isoformat(),
            "message": attempt.message, "result": result,
        }

    @staticmethod
    def _from_dict(value: object) -> PositionProtectionAttempt:
        if not isinstance(value, dict):
            raise TypeError("Protection attempt must be an object.")
        try:
            result = None
            if value.get("result") is not None:
                record = JsonFilePositionProtectionStore._from_dict({
                    "recorded_at": value["updated_at"],
                    "position_fill_ids": value["position_fill_ids"],
                    "result": value["result"],
                })
                result = record.result
            return PositionProtectionAttempt(
                attempt_id=value["attempt_id"], broker=value["broker"],
                symbol=value["symbol"],
                position_updated_at=datetime.fromisoformat(value["position_updated_at"]),
                position_fill_ids=tuple(value["position_fill_ids"]),
                status=PositionProtectionAttemptStatus(value["status"]),
                created_at=datetime.fromisoformat(value["created_at"]),
                updated_at=datetime.fromisoformat(value["updated_at"]),
                message=value["message"], result=result,
            )
        except KeyError as exc:
            raise ValueError(
                f"Protection attempt is missing field {exc.args[0]!r}."
            ) from exc

    @staticmethod
    def _key(broker, symbol, updated_at, fill_ids):
        if not isinstance(updated_at, datetime) or updated_at.tzinfo is None:
            raise ValueError("position_updated_at must be timezone-aware datetime.")
        if not isinstance(fill_ids, tuple) or not all(
            isinstance(item, str) for item in fill_ids
        ):
            raise TypeError("position_fill_ids must be a tuple of strings.")
        if not isinstance(broker, str) or not broker.strip():
            raise ValueError("broker must be a non-empty string.")
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        return (broker.strip().lower(), symbol.strip().upper(), updated_at,
                tuple(item.strip() for item in fill_ids if item.strip()))
