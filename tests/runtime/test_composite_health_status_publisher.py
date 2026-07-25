from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from imie.runtime import (
    CompositeHealthStatusPublisher,
    RuntimeHealthState,
    RuntimeHealthSummary,
)


NOW = datetime(
    2026,
    7,
    22,
    15,
    0,
    tzinfo=timezone.utc,
)


@dataclass
class RecordingStatusPublisher:
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


def make_summary() -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=RuntimeHealthState.RUNNING,
        started_at=NOW,
        checked_at=NOW,
        uptime_seconds=0.0,
        last_transition_at=NOW,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=0,
        error_type=None,
    )


def test_composite_publishes_to_all_publishers() -> None:
    first = RecordingStatusPublisher()
    second = RecordingStatusPublisher()

    publisher = CompositeHealthStatusPublisher(
        [
            first,
            second,
        ]
    )

    summary = make_summary()

    publisher.publish(
        summary
    )

    assert first.summaries == [
        summary
    ]
    assert second.summaries == [
        summary
    ]


def test_composite_requires_publishers() -> None:
    with pytest.raises(
        ValueError,
        match="empty",
    ):
        CompositeHealthStatusPublisher(
            []
        )