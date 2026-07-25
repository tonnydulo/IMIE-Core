from datetime import (
    datetime,
    timedelta,
    timezone,
)

import json

import pytest

from imie.runtime import (
    RuntimeHealthState,
    RuntimeHealthSummary,
)


STARTED_AT = datetime(
    2026,
    7,
    22,
    14,
    0,
    tzinfo=timezone.utc,
)

CHECKED_AT = (
    STARTED_AT
    + timedelta(
        minutes=5,
    )
)


def make_summary(
    *,
    state: RuntimeHealthState = (
        RuntimeHealthState.RUNNING
    ),
) -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=state,
        started_at=STARTED_AT,
        checked_at=CHECKED_AT,
        uptime_seconds=300.0,
        last_transition_at=STARTED_AT,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=2,
        error_type=None,
    )


def test_summary_can_be_created() -> None:
    summary = make_summary()

    assert (
        summary.state
        is RuntimeHealthState.RUNNING
    )
    assert summary.uptime_seconds == 300.0
    assert summary.completed_cycle_count == 2
    assert summary.running is True
    assert summary.terminal is False
    assert summary.failed is False


@pytest.mark.parametrize(
    "state",
    [
        RuntimeHealthState.STOPPED,
        RuntimeHealthState.FAILED,
    ],
)
def test_terminal_states(
    state: RuntimeHealthState,
) -> None:
    summary = make_summary(
        state=state
    )

    assert summary.terminal is True
    assert summary.running is False


def test_failed_property() -> None:
    summary = make_summary(
        state=RuntimeHealthState.FAILED
    )

    assert summary.failed is True


def test_checked_at_cannot_precede_start() -> None:
    with pytest.raises(
        ValueError,
        match="checked_at",
    ):
        RuntimeHealthSummary(
            state=RuntimeHealthState.CREATED,
            started_at=STARTED_AT,
            checked_at=(
                STARTED_AT
                - timedelta(
                    seconds=1,
                )
            ),
            uptime_seconds=0.0,
            last_transition_at=STARTED_AT,
            last_heartbeat_at=None,
            last_successful_cycle_at=None,
            completed_cycle_count=0,
            error_type=None,
        )

def make_populated_summary() -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=RuntimeHealthState.SLEEPING,
        started_at=STARTED_AT,
        checked_at=CHECKED_AT,
        uptime_seconds=300.0,
        last_transition_at=(
            STARTED_AT
            + timedelta(
                seconds=30,
            )
        ),
        last_heartbeat_at=(
            STARTED_AT
            + timedelta(
                seconds=240,
            )
        ),
        last_successful_cycle_at=(
            STARTED_AT
            + timedelta(
                seconds=180,
            )
        ),
        completed_cycle_count=4,
        error_type=None,
    )

def test_summary_serializes_to_dictionary() -> None:
    summary = make_populated_summary()

    payload = summary.to_dict()

    assert payload == {
        "state": "SLEEPING",
        "started_at": STARTED_AT.isoformat(),
        "checked_at": CHECKED_AT.isoformat(),
        "uptime_seconds": 300.0,
        "last_transition_at": (
            STARTED_AT
            + timedelta(
                seconds=30,
            )
        ).isoformat(),
        "last_heartbeat_at": (
            STARTED_AT
            + timedelta(
                seconds=240,
            )
        ).isoformat(),
        "last_successful_cycle_at": (
            STARTED_AT
            + timedelta(
                seconds=180,
            )
        ).isoformat(),
        "completed_cycle_count": 4,
        "error_type": None,
        "running": True,
        "terminal": False,
        "failed": False,
    }


def test_summary_dictionary_preserves_missing_timestamps() -> None:
    summary = make_summary()

    payload = summary.to_dict()

    assert payload["last_heartbeat_at"] is None
    assert (
        payload["last_successful_cycle_at"]
        is None
    )


def test_summary_serializes_to_compact_json() -> None:
    summary = make_populated_summary()

    payload = summary.to_json()

    assert "\n" not in payload
    assert ": " not in payload

    decoded = json.loads(
        payload
    )

    assert decoded == summary.to_dict()


def test_summary_serializes_to_pretty_json() -> None:
    summary = make_populated_summary()

    payload = summary.to_json(
        indent=2
    )

    assert "\n" in payload
    assert '  "checked_at"' in payload

    assert json.loads(
        payload
    ) == summary.to_dict()

@pytest.mark.parametrize(
    "indent",
    [
        True,
        False,
        2.5,
        "2",
    ],
)
def test_json_indent_must_be_int_or_none(
    indent: object,
) -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="indent",
    ):
        summary.to_json(
            indent=indent,  # type: ignore[arg-type]
        )

def test_json_indent_cannot_be_negative() -> None:
    summary = make_summary()

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        summary.to_json(
            indent=-1,
        )


def test_failed_summary_serialization() -> None:
    summary = RuntimeHealthSummary(
        state=RuntimeHealthState.FAILED,
        started_at=STARTED_AT,
        checked_at=CHECKED_AT,
        uptime_seconds=300.0,
        last_transition_at=CHECKED_AT,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=1,
        error_type="RuntimeError",
    )

    payload = summary.to_dict()

    assert payload["state"] == "FAILED"
    assert payload["error_type"] == "RuntimeError"
    assert payload["failed"] is True
    assert payload["terminal"] is True
    assert payload["running"] is False


def test_health_summary_dictionary_schema_is_stable() -> None:
    payload = make_summary().to_dict()

    assert set(
        payload
    ) == {
        "state",
        "started_at",
        "checked_at",
        "uptime_seconds",
        "last_transition_at",
        "last_heartbeat_at",
        "last_successful_cycle_at",
        "completed_cycle_count",
        "error_type",
        "running",
        "terminal",
        "failed",
    }