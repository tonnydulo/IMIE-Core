import json

from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import JsonFilePositionProtectionReconciliationStore
from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    PositionProtectionReconciliationRecord,
    PositionProtectionReconciliationResult,
)


POSITION_TIME = datetime(2026, 8, 14, 1, 0, tzinfo=timezone.utc)
OBSERVED = datetime(2026, 8, 14, 1, 1, tzinfo=timezone.utc)


def snapshot(order_id="target-1", status=BrokerOrderStatus.ACCEPTED):
    filled = 3 if status is BrokerOrderStatus.FILLED else 0
    return BrokerOrderSnapshot(
        broker="alpaca-paper",
        broker_order_id=order_id,
        symbol="NVDA",
        side="sell",
        order_type="limit",
        status=status,
        requested_quantity=3,
        filled_quantity=filled,
        remaining_quantity=3 - filled,
        average_fill_price=201.0 if filled else None,
        last_updated_at=OBSERVED,
        submitted_at=POSITION_TIME,
        accepted_at=POSITION_TIME,
        filled_at=OBSERVED if filled else None,
        warnings=("paper",),
    )


def record(*, observed_at=OBSERVED, state="active"):
    result = PositionProtectionReconciliationResult(
        broker="alpaca-paper",
        symbol="NVDA",
        state=state,
        requested_quantity=3,
        active_quantity=3 if state == "active" else 0,
        triggered_quantity=3 if state == "triggered" else 0,
        reconciled=True,
        snapshots=(
            snapshot(
                status=(
                    BrokerOrderStatus.FILLED
                    if state == "triggered"
                    else BrokerOrderStatus.ACCEPTED
                )
            ),
        ),
        warnings=("paper",),
    )
    return PositionProtectionReconciliationRecord(
        result=result,
        position_updated_at=POSITION_TIME,
        position_fill_ids=("fill-1",),
        observed_at=observed_at,
    )


def key():
    return {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "position_updated_at": POSITION_TIME,
        "position_fill_ids": ("fill-1",),
    }


def test_save_round_trips_complete_broker_truth(tmp_path):
    store = JsonFilePositionProtectionReconciliationStore(
        tmp_path / "reconciliations.json"
    )
    value = record()

    store.save(value)

    loaded = store.get_latest_for_position(**key())
    assert loaded == value
    assert loaded.result.snapshots[0].status is BrokerOrderStatus.ACCEPTED


def test_store_appends_observations_and_returns_latest(tmp_path):
    store = JsonFilePositionProtectionReconciliationStore(tmp_path / "store.json")
    first = record()
    second = record(
        observed_at=OBSERVED + timedelta(seconds=10), state="triggered"
    )

    store.save(first)
    store.save(second)

    assert store.list_for_position(**key()) == (first, second)
    assert store.get_latest_for_position(**key()) == second


def test_duplicate_observation_key_is_rejected(tmp_path):
    store = JsonFilePositionProtectionReconciliationStore(tmp_path / "store.json")
    store.save(record())

    with pytest.raises(ValueError, match="already exists"):
        store.save(record())


def test_query_does_not_create_missing_file(tmp_path):
    path = tmp_path / "store.json"
    store = JsonFilePositionProtectionReconciliationStore(path)

    assert store.get_latest_for_position(**key()) is None
    assert path.exists() is False


def test_malformed_json_fails_closed(tmp_path):
    path = tmp_path / "store.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="malformed JSON"):
        JsonFilePositionProtectionReconciliationStore(path).list_for_position(
            **key()
        )


def test_schema_and_records_are_explicit(tmp_path):
    path = tmp_path / "store.json"
    JsonFilePositionProtectionReconciliationStore(path).save(record())

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert len(payload["records"]) == 1
    assert payload["records"][0]["result"]["state"] == "active"
