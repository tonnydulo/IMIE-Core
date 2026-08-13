from __future__ import annotations

import json
import os

from datetime import datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

from imie.models import ExecutionPosition, PositionDirection


class JsonFilePositionStateStore:
    """Atomically persist the latest position for each broker and symbol."""

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

    def save(self, position: ExecutionPosition) -> None:
        if not isinstance(position, ExecutionPosition):
            raise TypeError("position must be an ExecutionPosition.")
        with self._lock:
            positions = list(self._load_positions())
            key = (position.broker, position.symbol)
            for index, current in enumerate(positions):
                if (current.broker, current.symbol) != key:
                    continue
                if position.last_updated_at < current.last_updated_at:
                    raise ValueError(
                        "Cannot overwrite position state with an older update."
                    )
                if position.last_updated_at == current.last_updated_at:
                    if position == current:
                        return
                    raise ValueError(
                        "Conflicting position state has the same update time."
                    )
                positions[index] = position
                break
            else:
                positions.append(position)
            self._write_positions(tuple(positions))

    def get(self, *, broker: str, symbol: str) -> ExecutionPosition | None:
        normalized_broker = self._required_text(broker, "broker").lower()
        normalized_symbol = self._required_text(symbol, "symbol").upper()
        with self._lock:
            for position in self._load_positions():
                if (position.broker, position.symbol) == (
                    normalized_broker,
                    normalized_symbol,
                ):
                    return position
        return None

    def _load_positions(self) -> tuple[ExecutionPosition, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Position store contains malformed JSON.") from exc
        if not isinstance(payload, dict):
            raise TypeError("Position store root must be an object.")
        if payload.get("schema_version") != self.schema_version:
            raise ValueError("Position store schema_version is unsupported.")
        values = payload.get("positions")
        if not isinstance(values, list):
            raise TypeError("Position store positions must be a list.")
        positions = tuple(self._position_from_dict(value) for value in values)
        keys = tuple((item.broker, item.symbol) for item in positions)
        if len(set(keys)) != len(keys):
            raise ValueError("Position store contains duplicate broker-symbol keys.")
        return positions

    def _write_positions(self, positions: tuple[ExecutionPosition, ...]) -> None:
        parent = self.path.parent
        if self.create_parent_directories:
            parent.mkdir(parents=True, exist_ok=True)
        elif not parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {parent}")
        payload = {
            "schema_version": self.schema_version,
            "positions": [self._position_to_dict(item) for item in positions],
        }
        serialized = json.dumps(
            payload, indent=self.indent, sort_keys=True, allow_nan=False
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
    def _position_to_dict(position: ExecutionPosition) -> dict[str, object]:
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
        }

    @staticmethod
    def _position_from_dict(value: object) -> ExecutionPosition:
        if not isinstance(value, dict):
            raise TypeError("Position store entry must be an object.")
        try:
            timestamp = value["last_updated_at"]
            if not isinstance(timestamp, str):
                raise TypeError("last_updated_at must be a string.")
            warnings = value.get("warnings", [])
            if not isinstance(warnings, list) or not all(
                isinstance(item, str) for item in warnings
            ):
                raise TypeError("Position store warnings must be a list of strings.")
            return ExecutionPosition(
                broker=value["broker"],
                symbol=value["symbol"],
                direction=PositionDirection(value["direction"]),
                quantity=value["quantity"],
                average_entry_price=value["average_entry_price"],
                market_price=value["market_price"],
                unrealized_pnl=value["unrealized_pnl"],
                realized_pnl=value["realized_pnl"],
                last_updated_at=datetime.fromisoformat(timestamp),
                warnings=tuple(warnings),
            )
        except KeyError as exc:
            raise ValueError(
                f"Position store entry is missing required field {exc.args[0]!r}."
            ) from exc

    @staticmethod
    def _required_text(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{name} cannot be empty.")
        return normalized
