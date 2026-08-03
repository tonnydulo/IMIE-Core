from datetime import datetime, timezone

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    CompositeResultPublisher,
)


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


def make_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="No new completed bar.",
    )


class RecordingPublisher:
    def __init__(
        self,
        name: str,
        events: list[str],
    ) -> None:
        self.name = name
        self.events = events
        self.results: list[
            AnalysisCycleResult
        ] = []

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.events.append(
            self.name
        )
        self.results.append(
            result
        )


class RaisingPublisher:
    def __init__(
        self,
        *,
        message: str,
        events: list[str] | None = None,
        name: str = "raising",
    ) -> None:
        self.message = message
        self.events = events
        self.name = name
        self.calls = 0

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        del result

        self.calls += 1

        if self.events is not None:
            self.events.append(
                self.name
            )

        raise ValueError(
            self.message
        )


def test_publisher_can_be_created() -> None:
    events: list[str] = []

    first = RecordingPublisher(
        "first",
        events,
    )

    second = RecordingPublisher(
        "second",
        events,
    )

    publisher = CompositeResultPublisher(
        publishers=[
            first,
            second,
        ],
    )

    assert publisher.publishers == (
        first,
        second,
    )
    assert publisher.continue_on_error is False


def test_publishers_must_be_iterable() -> None:
    with pytest.raises(
        TypeError,
        match="iterable",
    ):
        CompositeResultPublisher(
            publishers=object(),  # type: ignore[arg-type]
        )


def test_publishers_cannot_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="at least one",
    ):
        CompositeResultPublisher(
            publishers=[],
        )


def test_every_publisher_must_be_callable() -> None:
    with pytest.raises(
        TypeError,
        match="callable",
    ):
        CompositeResultPublisher(
            publishers=[
                lambda result: None,
                object(),
            ],
        )


def test_continue_on_error_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match="continue_on_error",
    ):
        CompositeResultPublisher(
            publishers=[
                lambda result: None,
            ],
            continue_on_error="yes",  # type: ignore[arg-type]
        )


def test_publish_forwards_result_in_order() -> None:
    events: list[str] = []

    first = RecordingPublisher(
        "first",
        events,
    )

    second = RecordingPublisher(
        "second",
        events,
    )

    third = RecordingPublisher(
        "third",
        events,
    )

    publisher = CompositeResultPublisher(
        publishers=[
            first,
            second,
            third,
        ],
    )

    result = make_result()

    publisher.publish(
        result
    )

    assert events == [
        "first",
        "second",
        "third",
    ]

    assert first.results == [
        result,
    ]
    assert second.results == [
        result,
    ]
    assert third.results == [
        result,
    ]


def test_publisher_is_callable() -> None:
    events: list[str] = []

    recorder = RecordingPublisher(
        "recorder",
        events,
    )

    publisher = CompositeResultPublisher(
        publishers=[
            recorder,
        ],
    )

    result = make_result()

    publisher(
        result
    )

    assert recorder.results == [
        result,
    ]


def test_result_must_be_analysis_cycle_result() -> None:
    publisher = CompositeResultPublisher(
        publishers=[
            lambda result: None,
        ],
    )

    with pytest.raises(
        TypeError,
        match="AnalysisCycleResult",
    ):
        publisher.publish(
            object(),  # type: ignore[arg-type]
        )


def test_failure_stops_later_publishers_by_default() -> None:
    events: list[str] = []

    first = RecordingPublisher(
        "first",
        events,
    )

    raising = RaisingPublisher(
        message="Publisher failed.",
        events=events,
    )

    final = RecordingPublisher(
        "final",
        events,
    )

    publisher = CompositeResultPublisher(
        publishers=[
            first,
            raising,
            final,
        ],
    )

    with pytest.raises(
        ValueError,
        match="Publisher failed",
    ):
        publisher.publish(
            make_result()
        )

    assert events == [
        "first",
        "raising",
    ]

    assert final.results == []


def test_continue_on_error_invokes_remaining_publishers() -> None:
    events: list[str] = []

    first = RecordingPublisher(
        "first",
        events,
    )

    raising = RaisingPublisher(
        message="Publisher failed.",
        events=events,
    )

    final = RecordingPublisher(
        "final",
        events,
    )

    publisher = CompositeResultPublisher(
        publishers=[
            first,
            raising,
            final,
        ],
        continue_on_error=True,
    )

    with pytest.raises(
        RuntimeError,
        match="One or more publishers failed",
    ):
        publisher.publish(
            make_result()
        )

    assert events == [
        "first",
        "raising",
        "final",
    ]

    assert len(
        final.results
    ) == 1


def test_continue_on_error_reports_all_failures() -> None:
    first_failure = RaisingPublisher(
        message="First failed.",
        name="first",
    )

    second_failure = RaisingPublisher(
        message="Second failed.",
        name="second",
    )

    publisher = CompositeResultPublisher(
        publishers=[
            first_failure,
            second_failure,
        ],
        continue_on_error=True,
    )

    with pytest.raises(
        RuntimeError,
    ) as exc_info:
        publisher.publish(
            make_result()
        )

    message = str(
        exc_info.value
    )

    assert "publisher 0" in message
    assert "First failed." in message
    assert "publisher 1" in message
    assert "Second failed." in message

    assert first_failure.calls == 1
    assert second_failure.calls == 1