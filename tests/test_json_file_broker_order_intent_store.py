import json
import os

from datetime import datetime, timezone
from pathlib import Path

import pytest

from imie.execution import (
    BrokerOrderIntentStore,
    JsonFileBrokerOrderIntentStore,
)
from imie.models import BrokerOrderIntentRecord, ExecutionOrderIntent


NOW = datetime(2026, 8, 13, 19, 0, tzinfo=timezone.utc)


def record(
    order_id: str = "order-123",
    quantity: int = 40,
) -> BrokerOrderIntentRecord:
    return BrokerOrderIntentRecord(
        broker="alpaca-paper",
        broker_order_id=order_id,
        recorded_at=NOW,
        submission_label="target1",
        intent=ExecutionOrderIntent(
            symbol="NVDA",
            side="buy",
            quantity=quantity,
            order_type="limit",
            entry_price=201.0,
            stop_price=200.0,
            target1_price=202.0,
            target2_price=203.0,
            time_in_force="day",
            valid=True,
            actionable=True,
            reasons=("Ready plan",),
            warnings=("Paper only",),
        ),
    )


def test_store_satisfies_contract_and_round_trips_exact_record(
    tmp_path: Path,
) -> None:
    store = JsonFileBrokerOrderIntentStore(tmp_path / "intents.json")
    original = record()

    assert isinstance(store, BrokerOrderIntentStore)
    assert store.get(
        broker="alpaca-paper", broker_order_id="missing"
    ) is None

    store.save(original)
    loaded = store.get(
        broker=" ALPACA-PAPER ", broker_order_id=" order-123 "
    )

    assert loaded == original
    assert loaded.intent.reasons == ("Ready plan",)
    assert loaded.intent.warnings == ("Paper only",)


def test_multiple_records_are_preserved(tmp_path: Path) -> None:
    store = JsonFileBrokerOrderIntentStore(tmp_path / "intents.json")
    store.save(record("order-1", 40))
    store.save(record("order-2", 60))

    assert store.get(
        broker="alpaca-paper", broker_order_id="order-1"
    ).intent.quantity == 40
    assert store.get(
        broker="alpaca-paper", broker_order_id="order-2"
    ).intent.quantity == 60


def test_duplicate_key_is_rejected_without_modifying_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "intents.json"
    store = JsonFileBrokerOrderIntentStore(path)
    store.save(record())
    before = path.read_bytes()

    with pytest.raises(ValueError, match="already exists"):
        store.save(record(quantity=60))

    assert path.read_bytes() == before


def test_write_is_flushed_before_atomic_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    original_fsync = os.fsync
    original_replace = os.replace

    def fsync(file_descriptor: int) -> None:
        events.append("fsync")
        original_fsync(file_descriptor)

    def replace(source, destination) -> None:
        events.append("replace")
        original_replace(source, destination)

    monkeypatch.setattr(os, "fsync", fsync)
    monkeypatch.setattr(os, "replace", replace)

    JsonFileBrokerOrderIntentStore(tmp_path / "intents.json").save(record())

    assert events == ["fsync", "replace"]


def test_failed_replace_cleans_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_replace(source, destination) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail_replace)
    path = tmp_path / "intents.json"

    with pytest.raises(OSError, match="replace failed"):
        JsonFileBrokerOrderIntentStore(path).save(record())

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("payload", "exception", "message"),
    [
        ("not-json", ValueError, "malformed JSON"),
        (json.dumps([]), TypeError, "root must be an object"),
        (
            json.dumps({"schema_version": 99, "records": []}),
            ValueError,
            "schema_version",
        ),
        (
            json.dumps({"schema_version": 1, "records": {}}),
            TypeError,
            "records must be a list",
        ),
    ],
)
def test_malformed_store_is_rejected(
    tmp_path: Path,
    payload: str,
    exception: type[Exception],
    message: str,
) -> None:
    path = tmp_path / "intents.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(exception, match=message):
        JsonFileBrokerOrderIntentStore(path).get(
            broker="alpaca-paper", broker_order_id="order-123"
        )


def test_duplicate_keys_in_existing_file_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "intents.json"
    store = JsonFileBrokerOrderIntentStore(path)
    store.save(record())
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["records"].append(payload["records"][0])
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate"):
        store.get(broker="alpaca-paper", broker_order_id="order-123")


def test_missing_parent_can_be_rejected(tmp_path: Path) -> None:
    store = JsonFileBrokerOrderIntentStore(
        tmp_path / "missing" / "intents.json",
        create_parent_directories=False,
    )

    with pytest.raises(FileNotFoundError, match="Parent directory"):
        store.save(record())

