import json

from datetime import datetime, timezone

import pytest

from imie.execution import JsonFileExecutionSubmissionReservationStore
from imie.models import ExecutionSubmissionReservation


NOW = datetime(2026, 8, 14, 5, 0, tzinfo=timezone.utc)
FIRST = "a" * 64
SECOND = "b" * 64


def reservation(fingerprint=FIRST, **overrides):
    values = {
        "fingerprint": fingerprint,
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 10,
        "reserved_at": NOW,
    }
    values.update(overrides)
    return ExecutionSubmissionReservation(**values)


def test_reservation_round_trips(tmp_path):
    store = JsonFileExecutionSubmissionReservationStore(tmp_path / "store.json")
    value = reservation()

    store.reserve(value)

    assert store.get(FIRST) == value


def test_exact_duplicate_is_rejected_without_changing_file(tmp_path):
    path = tmp_path / "store.json"
    store = JsonFileExecutionSubmissionReservationStore(path)
    store.reserve(reservation())
    before = path.read_bytes()

    with pytest.raises(ValueError, match="already reserved"):
        store.reserve(reservation(quantity=11))

    assert path.read_bytes() == before


def test_distinct_fingerprint_can_be_reserved(tmp_path):
    store = JsonFileExecutionSubmissionReservationStore(tmp_path / "store.json")
    first = reservation()
    second = reservation(SECOND, quantity=11)

    store.reserve(first)
    store.reserve(second)

    assert store.get(FIRST) == first
    assert store.get(SECOND) == second


def test_missing_query_does_not_create_file(tmp_path):
    path = tmp_path / "store.json"
    store = JsonFileExecutionSubmissionReservationStore(path)

    assert store.get(FIRST) is None
    assert path.exists() is False


def test_malformed_json_fails_closed(tmp_path):
    path = tmp_path / "store.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="malformed JSON"):
        JsonFileExecutionSubmissionReservationStore(path).get(FIRST)


def test_duplicate_persisted_fingerprints_fail_closed(tmp_path):
    path = tmp_path / "store.json"
    item = {
        "fingerprint": FIRST, "symbol": "NVDA", "side": "buy",
        "quantity": 10, "reserved_at": NOW.isoformat(),
    }
    path.write_text(json.dumps({
        "schema_version": 1, "reservations": [item, item]
    }), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicates"):
        JsonFileExecutionSubmissionReservationStore(path).get(FIRST)
