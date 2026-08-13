from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.models import ExecutionSubmissionReservation


class JsonFileExecutionSubmissionReservationStore:
    """Atomically reserve exact submissions before broker mutation."""

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

    def reserve(self, reservation: ExecutionSubmissionReservation) -> None:
        if not isinstance(reservation, ExecutionSubmissionReservation):
            raise TypeError("reservation must be an ExecutionSubmissionReservation.")
        with self._lock:
            reservations = self._load()
            if any(
                item.fingerprint == reservation.fingerprint
                for item in reservations
            ):
                raise ValueError("Execution submission fingerprint is already reserved.")
            self._write((*reservations, reservation))

    def get(self, fingerprint: str) -> ExecutionSubmissionReservation | None:
        normalized = self._fingerprint(fingerprint)
        with self._lock:
            return next(
                (item for item in self._load() if item.fingerprint == normalized),
                None,
            )

    def _load(self) -> tuple[ExecutionSubmissionReservation, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Submission reservation store contains malformed JSON.") from exc
        if not isinstance(payload, dict):
            raise TypeError("Submission reservation store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError("Submission reservation schema_version is unsupported.")
        values = payload.get("reservations")
        if not isinstance(values, list):
            raise TypeError("Submission reservations must be a list.")
        reservations = tuple(self._from_dict(item) for item in values)
        fingerprints = tuple(item.fingerprint for item in reservations)
        if len(set(fingerprints)) != len(fingerprints):
            raise ValueError("Submission reservation store contains duplicates.")
        return reservations

    def _write(
        self, reservations: tuple[ExecutionSubmissionReservation, ...]
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(
            {
                "schema_version": self.schema_version,
                "reservations": [self._to_dict(item) for item in reservations],
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
    def _to_dict(value: ExecutionSubmissionReservation) -> dict[str, object]:
        return {
            "fingerprint": value.fingerprint,
            "symbol": value.symbol,
            "side": value.side,
            "quantity": value.quantity,
            "reserved_at": value.reserved_at.isoformat(),
        }

    @staticmethod
    def _from_dict(value: object) -> ExecutionSubmissionReservation:
        if not isinstance(value, dict):
            raise TypeError("Submission reservation must be an object.")
        try:
            return ExecutionSubmissionReservation(
                fingerprint=value["fingerprint"],
                symbol=value["symbol"],
                side=value["side"],
                quantity=value["quantity"],
                reserved_at=datetime.fromisoformat(value["reserved_at"]),
            )
        except KeyError as exc:
            raise ValueError(
                f"Submission reservation is missing field {exc.args[0]!r}."
            ) from exc

    @staticmethod
    def _fingerprint(value: object) -> str:
        if not isinstance(value, str):
            raise TypeError("fingerprint must be a string.")
        normalized = value.strip().lower()
        if len(normalized) != 64 or any(
            character not in "0123456789abcdef" for character in normalized
        ):
            raise ValueError("fingerprint must be a SHA-256 hex digest.")
        return normalized
