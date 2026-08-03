import json

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

import pytest

from imie.runtime import (
    JsonHealthFilePublisher,
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


def make_summary(
    *,
    state: RuntimeHealthState = (
        RuntimeHealthState.RUNNING
    ),
    cycle_count: int = 1,
) -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=state,
        started_at=NOW,
        checked_at=NOW,
        uptime_seconds=0.0,
        last_transition_at=NOW,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=cycle_count,
        error_type=None,
    )


def test_publisher_writes_health_json(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "health.json"
    )

    publisher = JsonHealthFilePublisher(
        output_path
    )

    summary = make_summary()

    publisher.publish(
        summary
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload == summary.to_dict()


def test_publisher_creates_parent_directories(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "runtime"
        / "status"
        / "health.json"
    )

    publisher = JsonHealthFilePublisher(
        output_path
    )

    publisher.publish(
        make_summary()
    )

    assert output_path.exists()


def test_publisher_replaces_existing_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "health.json"
    )

    publisher = JsonHealthFilePublisher(
        output_path
    )

    publisher.publish(
        make_summary(
            state=RuntimeHealthState.RUNNING,
            cycle_count=1,
        )
    )

    publisher.publish(
        make_summary(
            state=RuntimeHealthState.SLEEPING,
            cycle_count=2,
        )
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["state"] == "SLEEPING"
    assert payload["completed_cycle_count"] == 2


def test_temporary_file_is_removed(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "health.json"
    )

    publisher = JsonHealthFilePublisher(
        output_path
    )

    publisher.publish(
        make_summary()
    )

    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )

    assert temporary_path.exists() is False


def test_compact_output_is_supported(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "health.json"
    )

    publisher = JsonHealthFilePublisher(
        output_path,
        indent=None,
    )

    publisher.publish(
        make_summary()
    )

    payload = output_path.read_text(
        encoding="utf-8"
    )

    assert ": " not in payload
    assert json.loads(
        payload
    )["state"] == "RUNNING"


def test_publish_requires_summary(
    tmp_path: Path,
) -> None:
    publisher = JsonHealthFilePublisher(
        tmp_path / "health.json"
    )

    with pytest.raises(
        TypeError,
        match="RuntimeHealthSummary",
    ):
        publisher.publish(
            object(),  # type: ignore[arg-type]
        )