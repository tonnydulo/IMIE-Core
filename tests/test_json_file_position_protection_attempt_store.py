from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    JsonFilePositionProtectionAttemptStore,
    PositionProtectionAttemptStore,
)
from imie.models import (
    PositionProtectionAttempt,
    PositionProtectionAttemptStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def reserved(*, attempt_id="attempt-1", fill_ids=("fill-1",)):
    return PositionProtectionAttempt(
        attempt_id=attempt_id, broker="alpaca-paper", symbol="NVDA",
        position_updated_at=NOW, position_fill_ids=fill_ids,
        status=PositionProtectionAttemptStatus.RESERVED,
        created_at=NOW, updated_at=NOW,
        message="Protection attempt reserved.",
    )


def terminal(value, status=PositionProtectionAttemptStatus.FAILED):
    return replace(
        value, status=status, updated_at=NOW + timedelta(seconds=1),
        message=f"Protection attempt {status.value}.",
    )


def test_store_satisfies_attempt_protocol(tmp_path):
    assert isinstance(
        JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json"),
        PositionProtectionAttemptStore,
    )


def test_reservation_round_trips_exactly(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "nested" / "attempts.json")
    expected = reserved()

    store.reserve(expected)

    assert store.get_for_position(
        broker="ALPACA-PAPER", symbol="nvda", position_updated_at=NOW,
        position_fill_ids=("fill-1",),
    ) == expected


@pytest.mark.parametrize(
    "status",
    [PositionProtectionAttemptStatus.FAILED,
     PositionProtectionAttemptStatus.UNCERTAIN],
)
def test_reserved_attempt_transitions_once_to_terminal_status(tmp_path, status):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")
    initial = reserved()
    expected = terminal(initial, status)
    store.reserve(initial)

    store.transition(expected)

    assert store.get_for_position(
        broker="alpaca-paper", symbol="NVDA", position_updated_at=NOW,
        position_fill_ids=("fill-1",),
    ) == expected


def test_duplicate_fingerprint_is_rejected_even_with_new_attempt_id(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")
    store.reserve(reserved())

    with pytest.raises(ValueError, match="already exists"):
        store.reserve(reserved(attempt_id="attempt-2"))


def test_terminal_attempt_cannot_transition_again(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")
    initial = reserved()
    store.reserve(initial)
    store.transition(terminal(initial))

    with pytest.raises(ValueError, match="cannot transition"):
        store.transition(terminal(initial, PositionProtectionAttemptStatus.UNCERTAIN))


def test_transition_fingerprint_must_match_reservation(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")
    initial = reserved()
    store.reserve(initial)
    changed = replace(
        terminal(initial), position_fill_ids=("fill-1", "fill-2")
    )

    with pytest.raises(ValueError, match="fingerprint"):
        store.transition(changed)


def test_unknown_attempt_cannot_transition(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")

    with pytest.raises(LookupError, match="No reserved"):
        store.transition(terminal(reserved()))


def test_new_fill_checkpoint_can_have_distinct_reservation(tmp_path):
    store = JsonFilePositionProtectionAttemptStore(tmp_path / "attempts.json")
    store.reserve(reserved())
    second = reserved(attempt_id="attempt-2", fill_ids=("fill-1", "fill-2"))

    store.reserve(second)

    assert store.get_for_position(
        broker="alpaca-paper", symbol="NVDA", position_updated_at=NOW,
        position_fill_ids=("fill-1", "fill-2"),
    ) == second
