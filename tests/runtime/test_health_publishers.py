from __future__ import annotations

import json
from datetime import (
    datetime,
    timezone,
)

import pytest

from imie.runtime import (
    CompositeHealthPublisher,
    ConsoleHealthPublisher,
    JsonLinesHealthPublisher,
    RuntimeHealthSnapshot,
    RuntimeHealthState,
    RuntimeHealthTracker,
)


NOW = datetime(
    2026,
    7,
    21,
    15,
    30,
    tzinfo=timezone.utc,
)


def make_snapshot(
    *,
    state: RuntimeHealthState = (
        RuntimeHealthState.RUNNING
    ),
    error_type: str | None = None,
) -> RuntimeHealthSnapshot:
    return RuntimeHealthSnapshot(
        state=state,
        changed_at=NOW,
        cycle_count=2,
        message="Runtime lifecycle changed.",
        error_type=error_type,
    )


def test_console_health_publisher_outputs_snapshot() -> None:
    output: list[str] = []

    publisher = ConsoleHealthPublisher(
        output=output.append,
    )

    publisher.publish(
        make_snapshot()
    )

    assert len(
        output
    ) == 1

    assert "RUNNING" in output[0]
    assert "cycles=2" in output[0]
    assert "Runtime lifecycle changed." in output[0]


def test_console_health_publisher_outputs_error_type() -> None:
    output: list[str] = []

    publisher = ConsoleHealthPublisher(
        output=output.append,
    )

    publisher.publish(
        make_snapshot(
            state=RuntimeHealthState.FAILED,
            error_type="RuntimeError",
        )
    )

    assert "error=RuntimeError" in output[0]


def test_json_lines_health_publisher_writes_record(
    tmp_path,
) -> None:
    file_path = (
        tmp_path
        / "health.jsonl"
    )

    publisher = JsonLinesHealthPublisher(
        file_path=file_path,
    )

    publisher.publish(
        make_snapshot()
    )

    lines = file_path.read_text(
        encoding="utf-8",
    ).splitlines()

    assert len(
        lines
    ) == 1

    payload = json.loads(
        lines[0]
    )

    assert payload == {
        "changed_at": NOW.isoformat(),
        "cycle_count": 2,
        "error_type": None,
        "message": "Runtime lifecycle changed.",
        "state": "RUNNING",
    }


class RecordingHealthPublisher:
    def __init__(
        self,
    ) -> None:
        self.snapshots: list[
            RuntimeHealthSnapshot
        ] = []

    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        self.snapshots.append(
            snapshot
        )


class RaisingHealthPublisher:
    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        del snapshot

        raise RuntimeError(
            "Health publish failed."
        )


def test_composite_publishes_to_all() -> None:
    first = RecordingHealthPublisher()
    second = RecordingHealthPublisher()

    publisher = CompositeHealthPublisher(
        publishers=(
            first,
            second,
        )
    )

    snapshot = make_snapshot()

    publisher.publish(
        snapshot
    )

    assert first.snapshots == [
        snapshot,
    ]

    assert second.snapshots == [
        snapshot,
    ]


def test_composite_can_continue_after_error() -> None:
    recording = RecordingHealthPublisher()

    publisher = CompositeHealthPublisher(
        publishers=(
            RaisingHealthPublisher(),
            recording,
        ),
        continue_on_error=True,
    )

    snapshot = make_snapshot()

    with pytest.raises(
        RuntimeError,
        match="One or more health publishers failed",
    ):
        publisher.publish(
            snapshot
        )

    assert recording.snapshots == [
        snapshot,
    ]


def test_composite_can_propagate_error() -> None:
    publisher = CompositeHealthPublisher(
        publishers=(
            RaisingHealthPublisher(),
        ),
        continue_on_error=False,
    )

    with pytest.raises(
        RuntimeError,
        match="Health publish failed",
    ):
        publisher.publish(
            make_snapshot()
        )


def test_json_lines_publisher_can_write_heartbeat(
    tmp_path,
) -> None:
    file_path = (
        tmp_path
        / "health.jsonl"
    )

    publisher = JsonLinesHealthPublisher(
        file_path=file_path,
    )

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    tracker.transition(
        RuntimeHealthState.SLEEPING,
        cycle_count=1,
        message="Runtime is sleeping.",
    )

    tracker.heartbeat(
        cycle_count=1,
    )

    lines = file_path.read_text(
        encoding="utf-8",
    ).splitlines()

    payloads = tuple(
        json.loads(
            line
        )
        for line in lines
    )

    assert len(
        payloads
    ) == 3

    heartbeat_payload = payloads[-1]

    assert heartbeat_payload["state"] == "SLEEPING"
    assert heartbeat_payload["cycle_count"] == 1
    assert (
        heartbeat_payload["message"]
        == "Runtime heartbeat."
    )