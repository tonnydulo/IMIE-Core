from __future__ import annotations

from dataclasses import dataclass, field

from datetime import (
    datetime,
    timezone,
    timedelta,
)

import pytest

from imie.runtime import (
    RuntimeHealthSnapshot,
    RuntimeHealthState,
    RuntimeHealthTracker,
)


NOW = datetime(
    2026,
    7,
    21,
    15,
    0,
    tzinfo=timezone.utc,
)


def test_health_snapshot_can_be_created() -> None:
    snapshot = RuntimeHealthSnapshot(
        state=RuntimeHealthState.RUNNING,
        changed_at=NOW,
        cycle_count=3,
        message="Runtime cycle active.",
    )

    assert (
        snapshot.state
        is RuntimeHealthState.RUNNING
    )
    assert snapshot.cycle_count == 3
    assert snapshot.failed is False
    assert snapshot.terminal is False


def test_failed_snapshot_is_terminal() -> None:
    snapshot = RuntimeHealthSnapshot(
        state=RuntimeHealthState.FAILED,
        changed_at=NOW,
        cycle_count=2,
        message="Runtime failed.",
        error_type="RuntimeError",
    )

    assert snapshot.failed is True
    assert snapshot.terminal is True


def test_stopped_snapshot_is_terminal() -> None:
    snapshot = RuntimeHealthSnapshot(
        state=RuntimeHealthState.STOPPED,
        changed_at=NOW,
        cycle_count=2,
        message="Runtime stopped.",
    )

    assert snapshot.terminal is True


def test_tracker_starts_in_created_state() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    assert (
        tracker.current.state
        is RuntimeHealthState.CREATED
    )
    assert len(
        tracker.history
    ) == 1


def test_tracker_records_transition() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    snapshot = tracker.transition(
        RuntimeHealthState.CONNECTED,
        cycle_count=0,
        message="Connected.",
    )

    assert tracker.current is snapshot
    assert len(
        tracker.history
    ) == 2


def test_tracker_records_error_type() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    snapshot = tracker.transition(
        RuntimeHealthState.FAILED,
        cycle_count=1,
        message="Runtime failed.",
        error=RuntimeError(
            "Failure."
        ),
    )

    assert snapshot.error_type == "RuntimeError"


def test_tracker_clock_must_return_aware_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        RuntimeHealthTracker(
            clock=lambda: datetime(
                2026,
                7,
                21,
                15,
                0,
            ),
        )


class RecordingPublisher:
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


def test_tracker_publishes_created_snapshot() -> None:
    publisher = RecordingPublisher()

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    assert publisher.snapshots == [
        tracker.current,
    ]


def test_tracker_publishes_each_transition() -> None:
    publisher = RecordingPublisher()

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    snapshot = tracker.transition(
        RuntimeHealthState.RUNNING,
        cycle_count=1,
        message="Running.",
    )

    assert publisher.snapshots == [
        tracker.history[0],
        snapshot,
    ]


def test_tracker_publisher_must_provide_publish() -> None:
    with pytest.raises(
        TypeError,
        match="publish",
    ):
        RuntimeHealthTracker(
            clock=lambda: NOW,
            publisher=object(),
        )


def test_heartbeat_uses_current_runtime_state() -> None:
    publisher = RecordingPublisher()

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    tracker.transition(
        RuntimeHealthState.SLEEPING,
        cycle_count=1,
        message="Runtime is sleeping.",
    )

    heartbeat = tracker.heartbeat(
        cycle_count=1,
    )

    assert (
        heartbeat.state
        is RuntimeHealthState.SLEEPING
    )

    assert heartbeat.cycle_count == 1
    assert heartbeat.message == "Runtime heartbeat."
    assert heartbeat.error_type is None

def test_heartbeat_does_not_append_lifecycle_history() -> None:
    publisher = RecordingPublisher()

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    tracker.transition(
        RuntimeHealthState.SLEEPING,
        cycle_count=1,
        message="Runtime is sleeping.",
    )

    history_before = tracker.history
    current_before = tracker.current

    heartbeat = tracker.heartbeat(
        cycle_count=1,
    )

    assert tracker.history == history_before
    assert tracker.current is current_before
    assert heartbeat is not tracker.current

def test_heartbeat_is_published() -> None:
    publisher = RecordingPublisher()

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        publisher=publisher,
    )

    published_before = len(
        publisher.snapshots
    )

    heartbeat = tracker.heartbeat(
        cycle_count=3,
        message="Runtime remains responsive.",
    )

    assert len(
        publisher.snapshots
    ) == published_before + 1

    assert publisher.snapshots[-1] is heartbeat
    assert heartbeat.cycle_count == 3
    assert (
        heartbeat.message
        == "Runtime remains responsive."
    )

def test_heartbeat_works_without_publisher() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    heartbeat = tracker.heartbeat(
        cycle_count=2,
    )

    assert (
        heartbeat.state
        is RuntimeHealthState.CREATED
    )

    assert heartbeat.cycle_count == 2
    assert len(
        tracker.history
    ) == 1

@pytest.mark.parametrize(
    "cycle_count",
    [
        True,
        False,
        1.5,
        "1",
        None,
    ],
)
def test_heartbeat_cycle_count_must_be_int(
    cycle_count: object,
) -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    with pytest.raises(
        TypeError,
        match="cycle_count",
    ):
        tracker.heartbeat(
            cycle_count=cycle_count,  # type: ignore[arg-type]
        )

def test_heartbeat_cycle_count_cannot_be_negative() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        tracker.heartbeat(
            cycle_count=-1,
        )

@pytest.mark.parametrize(
    "message",
    [
        "",
        "   ",
    ],
)
def test_heartbeat_message_cannot_be_empty(
    message: str,
) -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        tracker.heartbeat(
            cycle_count=0,
            message=message,
        )

def test_heartbeat_message_must_be_string() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    with pytest.raises(
        TypeError,
        match="message",
    ):
        tracker.heartbeat(
            cycle_count=0,
            message=123,  # type: ignore[arg-type]
        )


class SequencedClock:
    def __init__(
        self,
        *values: datetime,
    ) -> None:
        self._values = iter(
            values
        )

    def __call__(
        self,
    ) -> datetime:
        return next(
            self._values
        )
    
def test_tracker_exposes_start_time() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    assert tracker.started_at == NOW


def test_tracker_records_last_heartbeat_time() -> None:
    heartbeat_at = (
        NOW
        + timedelta(
            seconds=60,
        )
    )

    clock = SequencedClock(
        NOW,
        heartbeat_at,
    )

    tracker = RuntimeHealthTracker(
        clock=clock,
    )

    tracker.heartbeat(
        cycle_count=0,
    )

    assert (
        tracker.last_heartbeat_at
        == heartbeat_at
    )


def test_tracker_records_last_successful_cycle_time() -> None:
    cycle_at = (
        NOW
        + timedelta(
            seconds=5,
        )
    )

    clock = SequencedClock(
        NOW,
        cycle_at,
    )

    tracker = RuntimeHealthTracker(
        clock=clock,
    )

    recorded_at = (
        tracker.record_successful_cycle(
            cycle_count=1,
        )
    )

    assert recorded_at == cycle_at
    assert (
        tracker.last_successful_cycle_at
        == cycle_at
    )


def test_tracker_builds_health_summary() -> None:
    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
    )

    checked_at = (
        NOW
        + timedelta(
            minutes=10,
        )
    )

    summary = tracker.summary(
        checked_at=checked_at,
    )

    assert (
        summary.state
        is RuntimeHealthState.CREATED
    )
    assert summary.started_at == NOW
    assert summary.checked_at == checked_at
    assert summary.uptime_seconds == 600.0
    assert summary.completed_cycle_count == 0


def test_summary_includes_retained_telemetry() -> None:
    heartbeat_at = (
        NOW
        + timedelta(
            seconds=60,
        )
    )

    cycle_at = (
        NOW
        + timedelta(
            seconds=90,
        )
    )

    clock = SequencedClock(
        NOW,
        heartbeat_at,
        cycle_at,
    )

    tracker = RuntimeHealthTracker(
        clock=clock,
    )

    tracker.heartbeat(
        cycle_count=0,
    )

    tracker.record_successful_cycle(
        cycle_count=1,
    )

    summary = tracker.summary(
        checked_at=(
            NOW
            + timedelta(
                seconds=120,
            )
        ),
    )

    assert (
        summary.last_heartbeat_at
        == heartbeat_at
    )
    assert (
        summary.last_successful_cycle_at
        == cycle_at
    )


@dataclass
class RecordingHealthStatusPublisher:
    summaries: list[
        RuntimeHealthSummary
    ] = field(
        default_factory=list
    )

    def publish(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        self.summaries.append(
            summary
        )


def test_tracker_publishes_initial_status() -> None:
    publisher = (
        RecordingHealthStatusPublisher()
    )

    RuntimeHealthTracker(
        clock=lambda: NOW,
        status_publisher=publisher,
    )

    assert len(
        publisher.summaries
    ) == 1

    assert (
        publisher.summaries[0].state
        is RuntimeHealthState.CREATED
    )


def test_transition_publishes_health_summary() -> None:
    publisher = (
        RecordingHealthStatusPublisher()
    )

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        status_publisher=publisher,
    )

    tracker.transition(
        RuntimeHealthState.STARTING,
        cycle_count=0,
        message="Runtime starting.",
    )

    assert len(
        publisher.summaries
    ) == 2

    assert (
        publisher.summaries[-1].state
        is RuntimeHealthState.STARTING
    )

def test_heartbeat_publishes_health_summary() -> None:
    publisher = (
        RecordingHealthStatusPublisher()
    )

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        status_publisher=publisher,
    )

    tracker.transition(
        RuntimeHealthState.RUNNING,
        cycle_count=0,
        message="Runtime running.",
    )

    tracker.heartbeat(
        cycle_count=0,
    )

    summary = publisher.summaries[-1]

    assert (
        summary.state
        is RuntimeHealthState.RUNNING
    )
    assert summary.last_heartbeat_at == NOW

def test_successful_cycle_publishes_updated_count() -> None:
    publisher = (
        RecordingHealthStatusPublisher()
    )

    tracker = RuntimeHealthTracker(
        clock=lambda: NOW,
        status_publisher=publisher,
    )

    tracker.record_successful_cycle(
        cycle_count=1,
    )

    summary = publisher.summaries[-1]

    assert summary.completed_cycle_count == 1
    assert (
        summary.last_successful_cycle_at
        == NOW
    )