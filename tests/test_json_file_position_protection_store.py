import json

from datetime import datetime, timezone

import pytest

from imie.execution import JsonFilePositionProtectionStore, PositionProtectionStore
from imie.models import (
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionProtectionRecord,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def record(*, fill_ids=("fill-1",)):
    submissions = (
        ExistingPositionProtectionSubmission(
            label="target1", quantity=20, accepted=True,
            target_order_id="target-1", stop_order_id="stop-1",
            status="accepted", message="accepted",
        ),
        ExistingPositionProtectionSubmission(
            label="target2", quantity=20, accepted=True,
            target_order_id="target-2", stop_order_id="stop-2",
            status="accepted", message="accepted",
        ),
    )
    result = ExistingPositionProtectionResult(
        broker="alpaca-paper", symbol="NVDA", exit_side="sell",
        position_quantity=40, requested_quantity=40, accepted_quantity=40,
        position_updated_at=NOW, accepted=True, status="accepted",
        message="protected", submissions=submissions,
    )
    return PositionProtectionRecord(
        result=result,
        position_fill_ids=fill_ids,
        recorded_at=NOW,
    )


def test_store_satisfies_protocol(tmp_path):
    assert isinstance(
        JsonFilePositionProtectionStore(tmp_path / "protection.json"),
        PositionProtectionStore,
    )


def test_accepted_protection_round_trips_exactly(tmp_path):
    store = JsonFilePositionProtectionStore(tmp_path / "nested" / "protection.json")
    expected = record()

    store.save(expected)

    assert store.get_for_position(
        broker=" ALPACA-PAPER ", symbol=" nvda ",
        position_updated_at=NOW, position_fill_ids=("fill-1",),
    ) == expected
    assert json.loads(store.path.read_text())["schema_version"] == 1


def test_duplicate_position_fingerprint_is_rejected(tmp_path):
    store = JsonFilePositionProtectionStore(tmp_path / "protection.json")
    store.save(record())

    with pytest.raises(ValueError, match="already exists"):
        store.save(record())


def test_new_fill_checkpoint_is_a_distinct_position_fingerprint(tmp_path):
    store = JsonFilePositionProtectionStore(tmp_path / "protection.json")
    first = record()
    second = record(fill_ids=("fill-1", "fill-2"))

    store.save(first)
    store.save(second)

    assert store.get_for_position(
        broker="alpaca-paper", symbol="NVDA", position_updated_at=NOW,
        position_fill_ids=("fill-1", "fill-2"),
    ) == second


def test_missing_position_fingerprint_returns_none(tmp_path):
    store = JsonFilePositionProtectionStore(tmp_path / "protection.json")

    assert store.get_for_position(
        broker="alpaca-paper", symbol="NVDA", position_updated_at=NOW,
        position_fill_ids=("fill-1",),
    ) is None


def test_only_accepted_results_can_be_recorded():
    accepted = record().result
    rejected = ExistingPositionProtectionResult(
        broker=accepted.broker, symbol=accepted.symbol,
        exit_side=accepted.exit_side, position_quantity=40,
        requested_quantity=40, accepted_quantity=0,
        position_updated_at=NOW, accepted=False, status="rejected",
        message="rejected",
        submissions=tuple(
            ExistingPositionProtectionSubmission(
                label=item.label, quantity=item.quantity, accepted=False,
                target_order_id=None, stop_order_id=None,
                status="rejected", message="rejected",
            ) for item in accepted.submissions
        ),
    )

    with pytest.raises(ValueError, match="only accepted"):
        PositionProtectionRecord(
            result=rejected, position_fill_ids=("fill-1",), recorded_at=NOW
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        ("not json", ValueError),
        ("[]", TypeError),
        ('{"schema_version": 2, "records": []}', ValueError),
        ('{"schema_version": 1, "records": {}}', TypeError),
    ],
)
def test_invalid_store_payload_fails_closed(tmp_path, payload, error):
    path = tmp_path / "protection.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(error):
        JsonFilePositionProtectionStore(path).get_for_position(
            broker="alpaca-paper", symbol="NVDA",
            position_updated_at=NOW, position_fill_ids=("fill-1",),
        )


def test_duplicate_persisted_position_keys_fail_closed(tmp_path):
    path = tmp_path / "protection.json"
    value = JsonFilePositionProtectionStore._to_dict(record())
    path.write_text(json.dumps({"schema_version": 1, "records": [value, value]}))

    with pytest.raises(ValueError, match="duplicate position keys"):
        JsonFilePositionProtectionStore(path).get_for_position(
            broker="alpaca-paper", symbol="NVDA",
            position_updated_at=NOW, position_fill_ids=("fill-1",),
        )
