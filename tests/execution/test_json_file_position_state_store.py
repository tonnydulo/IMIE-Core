import json

from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import JsonFilePositionStateStore, PositionStateStore
from imie.models import ExecutionPosition, PositionDirection


NOW = datetime(2026, 8, 13, 12, 0, tzinfo=timezone.utc)


def position(
    *,
    updated_at=NOW,
    quantity=10,
    market_price=102.0,
    processed_fill_ids=("fill-1",),
):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=quantity,
        average_entry_price=100.0,
        market_price=market_price,
        unrealized_pnl=(market_price - 100.0) * quantity,
        realized_pnl=12.5,
        last_updated_at=updated_at,
        warnings=("paper",),
        processed_fill_ids=processed_fill_ids,
    )


def test_store_satisfies_position_state_protocol(tmp_path):
    assert isinstance(
        JsonFilePositionStateStore(tmp_path / "positions.json"),
        PositionStateStore,
    )


def test_missing_store_returns_none(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")

    assert store.get(broker="ALPACA-PAPER", symbol="nvda") is None


def test_position_round_trips_exactly(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "nested" / "positions.json")
    expected = position()

    store.save(expected)

    assert store.get(broker=" alpaca-paper ", symbol=" nvda ") == expected
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert len(payload["positions"]) == 1


def test_newer_position_replaces_existing_state(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")
    store.save(position())
    expected = position(
        updated_at=NOW + timedelta(seconds=1), quantity=12, market_price=101.0
    )

    store.save(expected)

    assert store.get(broker="alpaca-paper", symbol="NVDA") == expected
    assert len(json.loads(store.path.read_text())["positions"]) == 1


def test_stale_position_cannot_overwrite_broker_truth(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")
    current = position()
    store.save(current)
    original = store.path.read_bytes()

    with pytest.raises(ValueError, match="older update"):
        store.save(position(updated_at=NOW - timedelta(seconds=1)))

    assert store.path.read_bytes() == original


def test_identical_position_save_is_idempotent(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")
    expected = position()
    store.save(expected)
    original = store.path.read_bytes()

    store.save(expected)

    assert store.path.read_bytes() == original


def test_conflicting_same_timestamp_is_rejected(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")
    store.save(position())

    with pytest.raises(ValueError, match="same update time"):
        store.save(position(quantity=11))


def test_same_timestamp_accepts_monotonic_fill_checkpoint(tmp_path):
    store = JsonFilePositionStateStore(tmp_path / "positions.json")
    store.save(position())
    expected = position(
        quantity=11,
        processed_fill_ids=("fill-1", "fill-2"),
    )

    store.save(expected)

    assert store.get(broker="alpaca-paper", symbol="NVDA") == expected


def test_duplicate_persisted_keys_are_rejected(tmp_path):
    path = tmp_path / "positions.json"
    value = JsonFilePositionStateStore._position_to_dict(position())
    path.write_text(
        json.dumps({"schema_version": 1, "positions": [value, value]}),
        encoding="utf-8",
    )
    store = JsonFilePositionStateStore(path)

    with pytest.raises(ValueError, match="duplicate broker-symbol"):
        store.get(broker="alpaca-paper", symbol="NVDA")


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        ("not json", ValueError),
        ("[]", TypeError),
        ('{"schema_version": 2, "positions": []}', ValueError),
        ('{"schema_version": 1, "positions": {}}', TypeError),
    ],
)
def test_invalid_store_payload_is_rejected(tmp_path, payload, error):
    path = tmp_path / "positions.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(error):
        JsonFilePositionStateStore(path).get(
            broker="alpaca-paper", symbol="NVDA"
        )


def test_missing_parent_is_not_created_when_disabled(tmp_path):
    store = JsonFilePositionStateStore(
        tmp_path / "missing" / "positions.json",
        create_parent_directories=False,
    )

    with pytest.raises(FileNotFoundError):
        store.save(position())
